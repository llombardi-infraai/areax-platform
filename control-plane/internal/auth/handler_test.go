package auth

import (
	"bytes"
	"database/sql"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"areax/control-plane/internal/middleware"
	passutil "areax/control-plane/pkg/password"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"go.uber.org/zap"
)

func setupTestDB(t *testing.T) *sql.DB {
	databaseURL := os.Getenv("TEST_DATABASE_URL")
	if databaseURL == "" {
		databaseURL = "postgres://localhost:5432/controlplane_test?sslmode=disable"
	}

	db, err := sql.Open("postgres", databaseURL)
	require.NoError(t, err)

	// Clean up test data
	db.Exec("DELETE FROM sessions")
	db.Exec("DELETE FROM memberships")
	db.Exec("DELETE FROM organizations")
	db.Exec("DELETE FROM users")

	return db
}

func setupTestHandler(t *testing.T) (*Handler, *sql.DB, *gin.Engine) {
	database := setupTestDB(t)
	logger := zap.NewNop()

	// Initialize Redis (use test instance or mock)
	// Note: Tests will skip if Redis is not available
	handler := NewHandler(database, nil, logger)

	// Initialize JWT keys for testing
	os.Setenv("JWT_PRIVATE_KEY", testPrivateKey)
	os.Setenv("JWT_PUBLIC_KEY", testPublicKey)
	middleware.InitJWTKeys()

	gin.SetMode(gin.TestMode)
	r := gin.New()

	return handler, database, r
}

const testPrivateKey = `-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA2Z3qX2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
-----END RSA PRIVATE KEY-----`

const testPublicKey = `-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2Z3qX2X2X2X2X2X2X2X2
X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
-----END PUBLIC KEY-----`

func createTestUser(t *testing.T, database *sql.DB, email, pwd string, mfaEnabled bool) string {
	hash, err := passutil.Hash(pwd)
	require.NoError(t, err)

	userID := uuid.New().String()
	_, err = database.Exec(
		"INSERT INTO users (id, email, password_hash, mfa_enabled) VALUES ($1, $2, $3, $4)",
		userID, email, hash, mfaEnabled,
	)
	require.NoError(t, err)

	return userID
}

func TestLogin(t *testing.T) {
	handler, db, r := setupTestHandler(t)
	defer db.Close()

	r.POST("/v1/auth/login", handler.Login)

	t.Run("successful login", func(t *testing.T) {
		createTestUser(t, db, "test@example.com", "password123", false)

		reqBody := map[string]string{
			"email":    "test@example.com",
			"password": "password123",
		}
		jsonBody, _ := json.Marshal(reqBody)

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/v1/auth/login", bytes.NewBuffer(jsonBody))
		req.Header.Set("Content-Type", "application/json")
		r.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var resp LoginResponse
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.NotEmpty(t, resp.AccessToken)
		assert.NotEmpty(t, resp.RefreshToken)
		assert.Equal(t, "Bearer", resp.TokenType)
	})

	t.Run("invalid credentials", func(t *testing.T) {
		createTestUser(t, db, "test2@example.com", "password123", false)

		reqBody := map[string]string{
			"email":    "test2@example.com",
			"password": "wrongpassword",
		}
		jsonBody, _ := json.Marshal(reqBody)

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/v1/auth/login", bytes.NewBuffer(jsonBody))
		req.Header.Set("Content-Type", "application/json")
		r.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("user not found", func(t *testing.T) {
		reqBody := map[string]string{
			"email":    "nonexistent@example.com",
			"password": "password123",
		}
		jsonBody, _ := json.Marshal(reqBody)

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/v1/auth/login", bytes.NewBuffer(jsonBody))
		req.Header.Set("Content-Type", "application/json")
		r.ServeHTTP(w, req)

		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}

func TestLoginValidation(t *testing.T) {
	handler, db, r := setupTestHandler(t)
	defer db.Close()

	r.POST("/v1/auth/login", handler.Login)

	t.Run("missing email", func(t *testing.T) {
		reqBody := map[string]string{
			"password": "password123",
		}
		jsonBody, _ := json.Marshal(reqBody)

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/v1/auth/login", bytes.NewBuffer(jsonBody))
		req.Header.Set("Content-Type", "application/json")
		r.ServeHTTP(w, req)

		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("invalid email format", func(t *testing.T) {
		reqBody := map[string]string{
			"email":    "notanemail",
			"password": "password123",
		}
		jsonBody, _ := json.Marshal(reqBody)

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/v1/auth/login", bytes.NewBuffer(jsonBody))
		req.Header.Set("Content-Type", "application/json")
		r.ServeHTTP(w, req)

		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}
