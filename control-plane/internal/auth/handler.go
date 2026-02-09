package auth

import (
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"net/http"
	"time"

	"areax/control-plane/internal/db"
	"areax/control-plane/pkg/jwt"
	"areax/control-plane/pkg/password"
	"areax/control-plane/pkg/totp"

	"github.com/gin-gonic/gin"
	"github.com/redis/go-redis/v9"
	"go.uber.org/zap"
)

type Handler struct {
	db     *sql.DB
	rdb    *db.RedisClient
	logger *zap.Logger
}

func NewHandler(database *sql.DB, redisClient *db.RedisClient, logger *zap.Logger) *Handler {
	return &Handler{
		db:     database,
		rdb:    redisClient,
		logger: logger,
	}
}

type LoginRequest struct {
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required"`
	OrgID    string `json:"org_id,omitempty"`
	MFACode  string `json:"mfa_code,omitempty"`
}

type LoginResponse struct {
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token"`
	TokenType    string `json:"token_type"`
	ExpiresIn    int    `json:"expires_in"`
	MFARequired  bool   `json:"mfa_required,omitempty"`
}

type MFASetupResponse struct {
	Secret        string   `json:"secret"`
	QRCodeURL     string   `json:"qr_code_url"`
	RecoveryCodes []string `json:"recovery_codes"`
}

func (h *Handler) Login(c *gin.Context) {
	var req LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Find user by email
	var user db.User
	var mfaSecret sql.NullString
	var recoveryCodes sql.NullString
	err := h.db.QueryRow(
		"SELECT id, email, password_hash, mfa_secret, mfa_enabled, recovery_codes FROM users WHERE email = $1",
		req.Email,
	).Scan(&user.ID, &user.Email, &user.PasswordHash, &mfaSecret, &user.MFAEnabled, &recoveryCodes)

	if err == sql.ErrNoRows {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid credentials"})
		return
	}
	if err != nil {
		h.logger.Error("database error", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	if mfaSecret.Valid {
		user.MFASecret = &mfaSecret.String
	}

	// Verify password
	if err := password.Verify(req.Password, user.PasswordHash); err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid credentials"})
		return
	}

	// Check MFA if enabled
	if user.MFAEnabled {
		if req.MFACode == "" {
			c.JSON(http.StatusOK, LoginResponse{MFARequired: true})
			return
		}

		if user.MFASecret == nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "MFA not properly configured"})
			return
		}
		valid, err := totp.ValidateCode(req.MFACode, *user.MFASecret)
		if err != nil || !valid {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid MFA code"})
			return
		}
	}

	// Determine org_id
	var orgID *string
	if req.OrgID != "" {
		// Verify user has access to this org
		var membershipID string
		err := h.db.QueryRow(
			"SELECT id FROM memberships WHERE user_id = $1 AND org_id = $2",
			user.ID, req.OrgID,
		).Scan(&membershipID)
		if err != nil {
			c.JSON(http.StatusForbidden, gin.H{"error": "access denied to organization"})
			return
		}
		orgID = &req.OrgID
	}

	// Generate tokens
	accessToken, err := jwt.GenerateToken(user.ID, orgID, "access", 15*time.Minute)
	if err != nil {
		h.logger.Error("failed to generate access token", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	refreshToken, err := jwt.GenerateToken(user.ID, orgID, "refresh", 7*24*time.Hour)
	if err != nil {
		h.logger.Error("failed to generate refresh token", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	// Store session in Redis
	tokenHash := hashToken(refreshToken)
	expiresAt := time.Now().Add(7 * 24 * time.Hour)
	if err := h.rdb.SetSession(c.Request.Context(), tokenHash, user.ID, orgID, expiresAt); err != nil {
		h.logger.Error("failed to store session", zap.Error(err))
	}

	// Store session in database
	_, err = h.db.Exec(
		"INSERT INTO sessions (user_id, org_id, token_hash, expires_at) VALUES ($1, $2, $3, $4)",
		user.ID, orgID, tokenHash, expiresAt,
	)
	if err != nil {
		h.logger.Error("failed to store session in database", zap.Error(err))
	}

	c.JSON(http.StatusOK, LoginResponse{
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
		TokenType:    "Bearer",
		ExpiresIn:    900, // 15 minutes
	})
}

func (h *Handler) SetupMFA(c *gin.Context) {
	userID := c.GetString("user_id")

	// Generate TOTP secret
	secret, err := totp.GenerateSecret()
	if err != nil {
		h.logger.Error("failed to generate TOTP secret", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	// Generate recovery codes
	recoveryCodes, err := totp.GenerateRecoveryCodes(10)
	if err != nil {
		h.logger.Error("failed to generate recovery codes", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	// Get user email for QR code
	var email string
	if err := h.db.QueryRow("SELECT email FROM users WHERE id = $1", userID).Scan(&email); err != nil {
		h.logger.Error("failed to get user email", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	// Generate QR code URL
	qrURL := totp.GenerateQRCodeURL(secret, email, "AreaX")

	// Store secret temporarily (not enabled until verified)
	_, err = h.db.Exec(
		"UPDATE users SET mfa_secret = $1, recovery_codes = $2 WHERE id = $3",
		secret, recoveryCodes, userID,
	)
	if err != nil {
		h.logger.Error("failed to store MFA setup", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	c.JSON(http.StatusOK, MFASetupResponse{
		Secret:        secret,
		QRCodeURL:     qrURL,
		RecoveryCodes: recoveryCodes,
	})
}

func (h *Handler) VerifyMFA(c *gin.Context) {
	userID := c.GetString("user_id")

	var req struct {
		Code string `json:"code" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Get current MFA secret
	var secret string
	err := h.db.QueryRow("SELECT mfa_secret FROM users WHERE id = $1", userID).Scan(&secret)
	if err != nil {
		h.logger.Error("failed to get MFA secret", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	// Verify code
	valid, err := totp.ValidateCode(req.Code, secret)
	if err != nil || !valid {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid verification code"})
		return
	}

	// Enable MFA
	_, err = h.db.Exec("UPDATE users SET mfa_enabled = TRUE WHERE id = $1", userID)
	if err != nil {
		h.logger.Error("failed to enable MFA", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "MFA enabled successfully"})
}

func (h *Handler) RefreshToken(c *gin.Context) {
	var req struct {
		RefreshToken string `json:"refresh_token" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Parse and validate refresh token
	claims, err := jwt.ParseToken(req.RefreshToken)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid refresh token"})
		return
	}

	if claims.Type != "refresh" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid token type"})
		return
	}

	// Check if session exists in Redis
	tokenHash := hashToken(req.RefreshToken)
	session, err := h.rdb.GetSession(c.Request.Context(), tokenHash)
	if err != nil && err != redis.Nil {
		h.logger.Error("redis error", zap.Error(err))
	}

	if err == redis.Nil || len(session) == 0 {
		// Check database
		var sessionID string
		err := h.db.QueryRow(
			"SELECT id FROM sessions WHERE token_hash = $1 AND expires_at > NOW()",
			tokenHash,
		).Scan(&sessionID)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "session revoked or expired"})
			return
		}
	}

	// Generate new tokens
	accessToken, err := jwt.GenerateToken(claims.UserID, claims.OrgID, "access", 15*time.Minute)
	if err != nil {
		h.logger.Error("failed to generate access token", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	newRefreshToken, err := jwt.GenerateToken(claims.UserID, claims.OrgID, "refresh", 7*24*time.Hour)
	if err != nil {
		h.logger.Error("failed to generate refresh token", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	// Revoke old session and create new one
	newTokenHash := hashToken(newRefreshToken)
	expiresAt := time.Now().Add(7 * 24 * time.Hour)

	h.rdb.DeleteSession(c.Request.Context(), tokenHash)
	h.rdb.SetSession(c.Request.Context(), newTokenHash, claims.UserID, claims.OrgID, expiresAt)

	// Update database
	h.db.Exec("DELETE FROM sessions WHERE token_hash = $1", tokenHash)
	h.db.Exec(
		"INSERT INTO sessions (user_id, org_id, token_hash, expires_at) VALUES ($1, $2, $3, $4)",
		claims.UserID, claims.OrgID, newTokenHash, expiresAt,
	)

	c.JSON(http.StatusOK, LoginResponse{
		AccessToken:  accessToken,
		RefreshToken: newRefreshToken,
		TokenType:    "Bearer",
		ExpiresIn:    900,
	})
}

func (h *Handler) Logout(c *gin.Context) {
	userID := c.GetString("user_id")
	token := c.GetString("token")

	// Revoke session
	tokenHash := hashToken(token)
	h.rdb.DeleteSession(c.Request.Context(), tokenHash)
	h.db.Exec("DELETE FROM sessions WHERE token_hash = $1", tokenHash)

	h.logger.Info("user logged out", zap.String("user_id", userID))
	c.JSON(http.StatusOK, gin.H{"message": "logged out successfully"})
}

func (h *Handler) ListSessions(c *gin.Context) {
	userID := c.GetString("user_id")

	rows, err := h.db.Query(
		"SELECT id, user_id, org_id, created_at, expires_at FROM sessions WHERE user_id = $1 AND expires_at > NOW() ORDER BY created_at DESC",
		userID,
	)
	if err != nil {
		h.logger.Error("failed to list sessions", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}
	defer rows.Close()

	var sessions []db.SessionInfo
	for rows.Next() {
		var s db.SessionInfo
		var orgID sql.NullString
		if err := rows.Scan(&s.ID, &s.UserID, &orgID, &s.CreatedAt, &s.ExpiresAt); err != nil {
			continue
		}
		if orgID.Valid {
			s.OrgID = &orgID.String
		}
		sessions = append(sessions, s)
	}

	c.JSON(http.StatusOK, gin.H{"sessions": sessions})
}

func (h *Handler) RevokeSession(c *gin.Context) {
	userID := c.GetString("user_id")
	sessionID := c.Param("id")

	// Verify session belongs to user
	var tokenHash string
	err := h.db.QueryRow(
		"SELECT token_hash FROM sessions WHERE id = $1 AND user_id = $2",
		sessionID, userID,
	).Scan(&tokenHash)
	if err == sql.ErrNoRows {
		c.JSON(http.StatusNotFound, gin.H{"error": "session not found"})
		return
	}
	if err != nil {
		h.logger.Error("database error", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	// Revoke session
	h.rdb.DeleteSession(c.Request.Context(), tokenHash)
	h.db.Exec("DELETE FROM sessions WHERE id = $1", sessionID)

	c.JSON(http.StatusOK, gin.H{"message": "session revoked"})
}

func hashToken(token string) string {
	hash := sha256.Sum256([]byte(token))
	return hex.EncodeToString(hash[:])
}
