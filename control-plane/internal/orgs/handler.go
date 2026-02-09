package orgs

import (
	"database/sql"
	"net/http"

	"areax/control-plane/internal/db"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"go.uber.org/zap"
)

type Handler struct {
	db     *sql.DB
	logger *zap.Logger
}

func NewHandler(database *sql.DB, logger *zap.Logger) *Handler {
	return &Handler{
		db:     database,
		logger: logger,
	}
}

type CreateOrgRequest struct {
	Name          string `json:"name" binding:"required"`
	Slug          string `json:"slug" binding:"required"`
	Region        string `json:"region" binding:"required"`
	DatabaseHost  string `json:"database_host" binding:"required"`
	DatabaseName  string `json:"database_name" binding:"required"`
	StorageBucket string `json:"storage_bucket" binding:"required"`
}

type OrgResponse struct {
	ID        string `json:"id"`
	Name      string `json:"name"`
	Slug      string `json:"slug"`
	Region    string `json:"region"`
	Role      string `json:"role"`
	CreatedAt string `json:"created_at"`
}

func (h *Handler) ListOrgs(c *gin.Context) {
	userID := c.GetString("user_id")

	rows, err := h.db.Query(`
		SELECT o.id, o.name, o.slug, o.region, o.created_at, m.role 
		FROM organizations o
		JOIN memberships m ON o.id = m.org_id
		WHERE m.user_id = $1
		ORDER BY o.created_at DESC
	`, userID)
	if err != nil {
		h.logger.Error("failed to list organizations", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}
	defer rows.Close()

	var orgs []OrgResponse
	for rows.Next() {
		var org OrgResponse
		if err := rows.Scan(&org.ID, &org.Name, &org.Slug, &org.Region, &org.CreatedAt, &org.Role); err != nil {
			continue
		}
		orgs = append(orgs, org)
	}

	c.JSON(http.StatusOK, gin.H{"organizations": orgs})
}

func (h *Handler) CreateOrg(c *gin.Context) {
	userID := c.GetString("user_id")

	var req CreateOrgRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Check if slug is unique
	var existingID string
	err := h.db.QueryRow("SELECT id FROM organizations WHERE slug = $1", req.Slug).Scan(&existingID)
	if err != sql.ErrNoRows {
		if err == nil {
			c.JSON(http.StatusConflict, gin.H{"error": "organization slug already exists"})
			return
		}
		h.logger.Error("database error", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	tx, err := h.db.Begin()
	if err != nil {
		h.logger.Error("failed to begin transaction", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}
	defer tx.Rollback()

	// Create organization
	orgID := uuid.New().String()
	_, err = tx.Exec(`
		INSERT INTO organizations (id, name, slug, region, database_host, database_name, storage_bucket)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
	`, orgID, req.Name, req.Slug, req.Region, req.DatabaseHost, req.DatabaseName, req.StorageBucket)
	if err != nil {
		h.logger.Error("failed to create organization", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	// Create membership for creator as admin
	membershipID := uuid.New().String()
	_, err = tx.Exec(`
		INSERT INTO memberships (id, user_id, org_id, role)
		VALUES ($1, $2, $3, 'admin')
	`, membershipID, userID, orgID)
	if err != nil {
		h.logger.Error("failed to create membership", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	if err := tx.Commit(); err != nil {
		h.logger.Error("failed to commit transaction", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"id":   orgID,
		"name": req.Name,
		"slug": req.Slug,
		"role": "admin",
	})
}

func (h *Handler) GetRouting(c *gin.Context) {
	userID := c.GetString("user_id")
	orgID := c.Param("id")

	// Verify user has access to this org
	var membershipID string
	err := h.db.QueryRow(
		"SELECT id FROM memberships WHERE user_id = $1 AND org_id = $2",
		userID, orgID,
	).Scan(&membershipID)
	if err == sql.ErrNoRows {
		c.JSON(http.StatusForbidden, gin.H{"error": "access denied"})
		return
	}
	if err != nil {
		h.logger.Error("database error", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	// Get routing info
	var routing db.OrganizationRouting
	err = h.db.QueryRow(`
		SELECT database_host, database_name, storage_bucket, region
		FROM organizations
		WHERE id = $1
	`, orgID).Scan(&routing.DatabaseHost, &routing.DatabaseName, &routing.StorageBucket, &routing.Region)
	if err == sql.ErrNoRows {
		c.JSON(http.StatusNotFound, gin.H{"error": "organization not found"})
		return
	}
	if err != nil {
		h.logger.Error("database error", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	c.JSON(http.StatusOK, routing)
}
