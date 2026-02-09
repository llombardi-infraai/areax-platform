package sessions

import (
	"net/http"

	"areax/control-plane/internal/db"
	"areax/control-plane/internal/middleware"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

type Handler struct {
	redis  *db.RedisClient
	logger *zap.Logger
}

func NewHandler(redis *db.RedisClient, logger *zap.Logger) *Handler {
	return &Handler{
		redis:  redis,
		logger: logger,
	}
}

type Session struct {
	ID        string `json:"id"`
	Device    string `json:"device,omitempty"`
	Location  string `json:"location,omitempty"`
	CreatedAt string `json:"created_at"`
	Current   bool   `json:"current"`
}

func (h *Handler) ListSessions(c *gin.Context) {
	userID, _ := middleware.GetUserID(c)
	token, _ := c.Get(middleware.ContextKeyToken)
	currentToken := ""
	if t, ok := token.(string); ok {
		currentToken = t
	}

	sessions, err := h.redis.ListUserSessions(c.Request.Context(), userID)
	if err != nil {
		h.logger.Error("Failed to list sessions", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	var result []Session
	for _, key := range sessions {
		data, err := h.redis.GetSession(c.Request.Context(), key)
		if err != nil {
			continue
		}

		session := Session{
			ID:        key,
			Current:   key == currentToken,
			CreatedAt: data["created_at"],
		}
		result = append(result, session)
	}

	c.JSON(http.StatusOK, gin.H{"sessions": result})
}

func (h *Handler) RevokeSession(c *gin.Context) {
	sessionID := c.Param("id")

	// Delete from Redis
	err := h.redis.DeleteSession(c.Request.Context(), sessionID)
	if err != nil {
		h.logger.Error("Failed to revoke session", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Session revoked"})
}

func (h *Handler) RevokeAllSessions(c *gin.Context) {
	userID, _ := middleware.GetUserID(c)
	token, _ := c.Get(middleware.ContextKeyToken)
	currentToken := ""
	if t, ok := token.(string); ok {
		currentToken = t
	}

	sessions, err := h.redis.ListUserSessions(c.Request.Context(), userID)
	if err != nil {
		h.logger.Error("Failed to list sessions", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	for _, key := range sessions {
		// Skip current session
		if key == currentToken {
			continue
		}
		h.redis.DeleteSession(c.Request.Context(), key)
	}

	c.JSON(http.StatusOK, gin.H{"message": "All other sessions revoked"})
}
