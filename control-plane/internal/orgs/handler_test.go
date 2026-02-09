package orgs

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

const testPrivateKey = `-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA0Z3VS5JJcds3xfn/ygWyF8PbnGy0AHB7MqK8k7f5a3x8KL5y
sTy2QsR8h1F8fR9G8f5Y3f4X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2
X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2
X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
-----END RSA PRIVATE KEY-----`

const testPublicKey = `-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0Z3VS5JJcds3xfn/ygWy
F8PbnGy0AHB7MqK8k7f5a3x8KL5ysTy2QsR8h1F8fR9G8f5Y3f4X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2
X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X2X
-----END PUBLIC KEY-----`

func createTestUser(t *testing.T, database *sql.DB, email, pwd string) string {
	hash, err := passutil.Hash(pwd)
	require.NoError(t, err)

	userID := uuid.New().String()
	_, err = database.Exec(
		"INSERT INTO users (id, email, password_hash, mfa_enabled) VALUES ($1, $2, $3, $4)",
		userID, email, hash, false,
	)
	require.NoError(t, err)

	return userID
}

func createTestOrg(t *testing.T, database *sql.DB, name, slug string) string {
	orgID := uuid.New().String()
	_, err := database.Exec(
		"INSERT INTO organizations (id, name, slug, region, database_host, database_name, storage_bucket) VALUES ($1, $2, $3, $4, $5, $6, $7)",
		orgID, name, slug, "us-east-1", "db.example.com", slug+"_db", slug+"-bucket",
	)
	require.NoError(t, err)
	return orgID
}

func createMembership(t *testing.T, database *sql.DB, userID, orgID, role string) {
	membershipID := uuid.New().String()
	_, err := database.Exec(
		"INSERT INTO memberships (id, user_id, org_id, role) VALUES ($1, $2, $3, $4)",
		membershipID, userID, orgID, role,
	)
	require.NoError(t, err)
}

func setupTestHandler(t *testing.T) (*Handler, *sql.DB, *gin.Engine) {
	db := setupTestDB(t)
	logger := zap.NewNop()

	handler := NewHandler(db, logger)

	// Initialize JWT keys for testing
	os.Setenv("JWT_PRIVATE_KEY", testPrivateKey)
	os.Setenv("JWT_PUBLIC_KEY", testPublicKey)
	middleware.InitJWTKeys()

	gin.SetMode(gin.TestMode)
	r := gin.New()

	return handler, db, r
}

func TestListOrgs(t *testing.T) {
	handler, db, r := setupTestHandler(t)
	defer db.Close()

	userID := createTestUser(t, db, "test@example.com", "password123")
	orgID := createTestOrg(t, db, "Test Org", "test-org")
	createMembership(t, db, userID, orgID, "admin")

	r.GET("/v1/orgs", func(c *gin.Context) {
		c.Set("user_id", userID)
		handler.ListOrgs(c)
	})

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/v1/orgs", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var resp struct {
		Organizations []OrgResponse `json:"organizations"`
	}
	err := json.Unmarshal(w.Body.Bytes(), &resp)
	require.NoError(t, err)
	assert.Len(t, resp.Organizations, 1)
	assert.Equal(t, "Test Org", resp.Organizations[0].Name)
	assert.Equal(t, "admin", resp.Organizations[0].Role)
}

func TestCreateOrg(t *testing.T) {
	handler, db, r := setupTestHandler(t)
	defer db.Close()

	userID := createTestUser(t, db, "test@example.com", "password123")

	r.POST("/v1/orgs", func(c *gin.Context) {
		c.Set("user_id", userID)
		handler.CreateOrg(c)
	})

	t.Run("successful creation", func(t *testing.T) {
		reqBody := CreateOrgRequest{
			Name:          "New Org",
			Slug:          "new-org",
			Region:        "us-west-2",
			DatabaseHost:  "db.example.com",
			DatabaseName:  "new_org_db",
			StorageBucket: "new-org-bucket",
		}
		jsonBody, _ := json.Marshal(reqBody)

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/v1/orgs", bytes.NewBuffer(jsonBody))
		req.Header.Set("Content-Type", "application/json")
		r.ServeHTTP(w, req)

		assert.Equal(t, http.StatusCreated, w.Code)

		var resp map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.NotEmpty(t, resp["id"])
		assert.Equal(t, "New Org", resp["name"])
		assert.Equal(t, "admin", resp["role"])
	})

	t.Run("duplicate slug", func(t *testing.T) {
		// First create an org
		reqBody := CreateOrgRequest{
			Name:          "Another Org",
			Slug:          "duplicate-slug",
			Region:        "us-west-2",
			DatabaseHost:  "db.example.com",
			DatabaseName:  "another_db",
			StorageBucket: "another-bucket",
		}
		jsonBody, _ := json.Marshal(reqBody)

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/v1/orgs", bytes.NewBuffer(jsonBody))
		req.Header.Set("Content-Type", "application/json")
		r.ServeHTTP(w, req)
		assert.Equal(t, http.StatusCreated, w.Code)

		// Try to create another with same slug
		w = httptest.NewRecorder()
		req, _ = http.NewRequest("POST", "/v1/orgs", bytes.NewBuffer(jsonBody))
		req.Header.Set("Content-Type", "application/json")
		r.ServeHTTP(w, req)

		assert.Equal(t, http.StatusConflict, w.Code)
	})
}

func TestGetRouting(t *testing.T) {
	handler, db, r := setupTestHandler(t)
	defer db.Close()

	userID := createTestUser(t, db, "test@example.com", "password123")
	orgID := createTestOrg(t, db, "Test Org", "test-org")
	createMembership(t, db, userID, orgID, "member")

	r.GET("/v1/orgs/:id/routing", func(c *gin.Context) {
		c.Set("user_id", userID)
		handler.GetRouting(c)
	})

	t.Run("successful routing", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/v1/orgs/"+orgID+"/routing", nil)
		r.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var resp struct {
			DatabaseHost  string `json:"database_host"`
			DatabaseName  string `json:"database_name"`
			StorageBucket string `json:"storage_bucket"`
			Region        string `json:"region"`
		}
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.Equal(t, "db.example.com", resp.DatabaseHost)
		assert.Equal(t, "test-org_db", resp.DatabaseName)
		assert.Equal(t, "test-org-bucket", resp.StorageBucket)
	})

	t.Run("access denied", func(t *testing.T) {
		otherUserID := createTestUser(t, db, "other@example.com", "password123")
		_ = createTestOrg(t, db, "Other Org", "other-org")
		// Don't create membership for first user

		r2 := gin.New()
		r2.GET("/v1/orgs/:id/routing", func(c *gin.Context) {
			c.Set("user_id", otherUserID)
			handler.GetRouting(c)
		})

		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/v1/orgs/"+orgID+"/routing", nil)
		r2.ServeHTTP(w, req)

		assert.Equal(t, http.StatusForbidden, w.Code)
	})

	t.Run("org not found", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/v1/orgs/"+uuid.New().String()+"/routing", nil)
		r.ServeHTTP(w, req)

		assert.Equal(t, http.StatusForbidden, w.Code)
	})
}
