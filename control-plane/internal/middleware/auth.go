package middleware

import (
	"net/http"
	"strings"

	"areax/control-plane/pkg/jwt"
	"github.com/gin-gonic/gin"
)

const ContextKeyUserID = "userID"
const ContextKeyOrgID = "orgID"
const ContextKeyToken = "token"

var jwtPublicKeyPEM string

func InitJWTKeys() error {
	// In production, load from environment variables or secrets manager
	// For now, we'll use a simple approach
	return nil
}

func AuthRequired() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Authorization header required"})
			c.Abort()
			return
		}

		parts := strings.SplitN(authHeader, " ", 2)
		if len(parts) != 2 || strings.ToLower(parts[0]) != "bearer" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid authorization header format"})
			c.Abort()
			return
		}

		tokenString := parts[1]
		claims, err := jwt.ParseToken(tokenString)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid or expired token"})
			c.Abort()
			return
		}

		if claims.Type != "access" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token type"})
			c.Abort()
			return
		}

		c.Set(ContextKeyUserID, claims.UserID)
		if claims.OrgID != nil {
			c.Set(ContextKeyOrgID, *claims.OrgID)
		}
		c.Set(ContextKeyToken, tokenString)

		c.Next()
	}
}

func OptionalAuth() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.Next()
			return
		}

		parts := strings.SplitN(authHeader, " ", 2)
		if len(parts) != 2 || strings.ToLower(parts[0]) != "bearer" {
			c.Next()
			return
		}

		tokenString := parts[1]
		claims, err := jwt.ParseToken(tokenString)
		if err != nil {
			c.Next()
			return
		}

		c.Set(ContextKeyUserID, claims.UserID)
		if claims.OrgID != nil {
			c.Set(ContextKeyOrgID, *claims.OrgID)
		}

		c.Next()
	}
}

func GetUserID(c *gin.Context) (string, bool) {
	userID, exists := c.Get(ContextKeyUserID)
	if !exists {
		return "", false
	}
	return userID.(string), true
}

func GetOrgID(c *gin.Context) (string, bool) {
	orgID, exists := c.Get(ContextKeyOrgID)
	if !exists {
		return "", false
	}
	return orgID.(string), true
}
