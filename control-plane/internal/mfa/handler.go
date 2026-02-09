package mfa

import (
	"crypto/rand"
	"database/sql"
	"encoding/base32"
	"net/http"
	"time"

	"areax/control-plane/internal/db"
	"areax/control-plane/internal/middleware"
	"areax/control-plane/pkg/jwt"
	"areax/control-plane/pkg/totp"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

type Handler struct {
	db     *sql.DB
	redis  *db.RedisClient
	logger *zap.Logger
}

func NewHandler(db *sql.DB, redis *db.RedisClient, logger *zap.Logger) *Handler {
	return &Handler{
		db:     db,
		redis:  redis,
		logger: logger,
	}
}

type SetupMFAResponse struct {
	Secret   string   `json:"secret"`
	QRCode   string   `json:"qr_code"`
	BackupCodes []string `json:"backup_codes"`
}

func (h *Handler) SetupMFA(c *gin.Context) {
	userID, _ := middleware.GetUserID(c)

	// Generate new TOTP secret
	secret := make([]byte, 32)
	if _, err := rand.Read(secret); err != nil {
		h.logger.Error("Failed to generate secret", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}
	secretStr := base32.StdEncoding.EncodeToString(secret)

	// Generate backup codes
	backupCodes := generateBackupCodes(10)

	// Get user email for QR code
	var email string
	err := h.db.QueryRow("SELECT email FROM users WHERE id = $1", userID).Scan(&email)
	if err != nil {
		h.logger.Error("Failed to get user email", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	// Generate QR code URL
	qrURL := totp.GenerateQRCodeURL(email, "Area X", secretStr)

	// Temporarily store secret (not enabled until verified)
	_, err = h.db.Exec(
		"UPDATE users SET mfa_secret = $1, recovery_codes = $2 WHERE id = $3",
		secretStr, backupCodes, userID,
	)
	if err != nil {
		h.logger.Error("Failed to save MFA setup", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	c.JSON(http.StatusOK, SetupMFAResponse{
		Secret:      secretStr,
		QRCode:      qrURL,
		BackupCodes: backupCodes,
	})
}

type VerifyMFARequest struct {
	Code     string `json:"code" binding:"required"`
	UserID   string `json:"user_id,omitempty"`
	SetupMode bool   `json:"setup_mode,omitempty"`
}

type VerifyMFAResponse struct {
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token"`
	TokenType    string `json:"token_type"`
	ExpiresIn    int    `json:"expires_in"`
}

func (h *Handler) VerifyMFA(c *gin.Context) {
	var req VerifyMFARequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	var userID string
	if req.SetupMode {
		// For setup verification, get user from auth context
		uid, _ := middleware.GetUserID(c)
		userID = uid
	} else {
		// For login, user_id should be provided
		userID = req.UserID
	}

	// Get user's MFA secret
	var secret string
	var mfaEnabled bool
	err := h.db.QueryRow(
		"SELECT mfa_secret, mfa_enabled FROM users WHERE id = $1",
		userID,
	).Scan(&secret, &mfaEnabled)

	if err == sql.ErrNoRows {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}
	if err != nil {
		h.logger.Error("Database error", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	// If MFA not set up
	if secret == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "MFA not set up"})
		return
	}

	// Validate TOTP code
	valid, err := totp.ValidateCode(req.Code, secret)
	if err != nil || !valid {
		// Try backup codes
		var recoveryCodes []string
		err := h.db.QueryRow(
			"SELECT recovery_codes FROM users WHERE id = $1",
			userID,
		).Scan(&recoveryCodes)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid code"})
			return
		}

		// Check if code matches a backup code
		backupCodeUsed := false
		newCodes := make([]string, 0, len(recoveryCodes))
		for _, code := range recoveryCodes {
			if code == req.Code {
				backupCodeUsed = true
			} else {
				newCodes = append(newCodes, code)
			}
		}

		if !backupCodeUsed {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid code"})
			return
		}

		// Remove used backup code
		_, _ = h.db.Exec(
			"UPDATE users SET recovery_codes = $1 WHERE id = $2",
			newCodes, userID,
		)
	}

	// If in setup mode, enable MFA
	if req.SetupMode && !mfaEnabled {
		_, err = h.db.Exec(
			"UPDATE users SET mfa_enabled = true WHERE id = $1",
			userID,
		)
		if err != nil {
			h.logger.Error("Failed to enable MFA", zap.Error(err))
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			return
		}
	}

	// Generate tokens
	tokens, err := h.generateTokens(userID, nil)
	if err != nil {
		h.logger.Error("Failed to generate tokens", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	c.JSON(http.StatusOK, tokens)
}

func generateBackupCodes(count int) []string {
	codes := make([]string, count)
	for i := 0; i < count; i++ {
		b := make([]byte, 10)
		rand.Read(b)
		codes[i] = base32.StdEncoding.EncodeToString(b)[:8]
	}
	return codes
}

func (h *Handler) generateTokens(userID string, orgID *string) (*VerifyMFAResponse, error) {
	accessToken, err := jwt.GenerateToken(userID, orgID, "access", 15*time.Minute)
	if err != nil {
		return nil, err
	}

	refreshToken, err := jwt.GenerateToken(userID, orgID, "refresh", 7*24*time.Hour)
	if err != nil {
		return nil, err
	}

	return &VerifyMFAResponse{
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
		TokenType:    "Bearer",
		ExpiresIn:    900,
	}, nil
}
