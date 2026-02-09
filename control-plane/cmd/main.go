package main

import (
	"log"
	"os"

	"areax/control-plane/internal/auth"
	"areax/control-plane/internal/db"
	"areax/control-plane/internal/middleware"
	"areax/control-plane/internal/orgs"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"go.uber.org/zap"
)

func main() {
	// Load .env file if it exists
	_ = godotenv.Load()

	// Initialize logger
	logger, err := zap.NewProduction()
	if err != nil {
		log.Fatalf("Failed to initialize logger: %v", err)
	}
	defer logger.Sync()

	// Initialize database
	database, err := db.InitDB()
	if err != nil {
		logger.Fatal("Failed to initialize database", zap.Error(err))
	}
	defer database.Close()

	// Run migrations
	if err := db.RunMigrations(database); err != nil {
		logger.Fatal("Failed to run migrations", zap.Error(err))
	}

	// Initialize Redis
	rdb, err := db.InitRedis()
	if err != nil {
		logger.Fatal("Failed to initialize Redis", zap.Error(err))
	}
	defer rdb.Close()

	// Initialize JWT keys
	if err := middleware.InitJWTKeys(); err != nil {
		logger.Fatal("Failed to initialize JWT keys", zap.Error(err))
	}

	// Setup Gin
	r := gin.New()
	r.Use(middleware.Logger(logger))
	r.Use(middleware.Recovery(logger))
	r.Use(middleware.CORS())

	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "healthy"})
	})

	// API v1 routes
	v1 := r.Group("/v1")

	// Auth routes
	authHandler := auth.NewHandler(database, rdb, logger)
	authRoutes := v1.Group("/auth")
	{
		authRoutes.POST("/login", authHandler.Login)
		authRoutes.POST("/mfa/setup", middleware.AuthRequired(), authHandler.SetupMFA)
		authRoutes.POST("/mfa/verify", middleware.AuthRequired(), authHandler.VerifyMFA)
		authRoutes.POST("/refresh", authHandler.RefreshToken)
		authRoutes.POST("/logout", middleware.AuthRequired(), authHandler.Logout)
		authRoutes.GET("/sessions", middleware.AuthRequired(), authHandler.ListSessions)
		authRoutes.DELETE("/sessions/:id", middleware.AuthRequired(), authHandler.RevokeSession)
	}

	// Organization routes
	orgHandler := orgs.NewHandler(database, logger)
	orgRoutes := v1.Group("/orgs")
	{
		orgRoutes.GET("", middleware.AuthRequired(), orgHandler.ListOrgs)
		orgRoutes.POST("", middleware.AuthRequired(), orgHandler.CreateOrg)
		orgRoutes.GET("/:id/routing", middleware.AuthRequired(), orgHandler.GetRouting)
	}

	// Get port from environment
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	logger.Info("Starting server", zap.String("port", port))
	if err := r.Run(":" + port); err != nil {
		logger.Fatal("Failed to start server", zap.Error(err))
	}
}
