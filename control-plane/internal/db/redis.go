package db

import (
	"context"
	"fmt"
	"os"
	"time"

	"github.com/redis/go-redis/v9"
)

type RedisClient struct {
	client *redis.Client
}

func InitRedis() (*RedisClient, error) {
	redisURL := os.Getenv("REDIS_URL")
	if redisURL == "" {
		redisURL = "localhost:6379"
	}

	opts, err := redis.ParseURL(redisURL)
	if err != nil {
		opts = &redis.Options{
			Addr: redisURL,
		}
	}

	client := redis.NewClient(opts)

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := client.Ping(ctx).Err(); err != nil {
		return nil, fmt.Errorf("failed to ping redis: %w", err)
	}

	return &RedisClient{client: client}, nil
}

func (r *RedisClient) Close() error {
	return r.client.Close()
}

func (r *RedisClient) Client() *redis.Client {
	return r.client
}

func (r *RedisClient) SetSession(ctx context.Context, tokenHash string, userID string, orgID *string, expiresAt time.Time) error {
	key := fmt.Sprintf("session:%s", tokenHash)
	data := map[string]interface{}{
		"user_id": userID,
		"expires_at": expiresAt.Unix(),
	}
	if orgID != nil {
		data["org_id"] = *orgID
	}
	
	pipe := r.client.Pipeline()
	pipe.HSet(ctx, key, data)
	pipe.ExpireAt(ctx, key, expiresAt)
	_, err := pipe.Exec(ctx)
	return err
}

func (r *RedisClient) GetSession(ctx context.Context, tokenHash string) (map[string]string, error) {
	key := fmt.Sprintf("session:%s", tokenHash)
	return r.client.HGetAll(ctx, key).Result()
}

func (r *RedisClient) DeleteSession(ctx context.Context, tokenHash string) error {
	key := fmt.Sprintf("session:%s", tokenHash)
	return r.client.Del(ctx, key).Err()
}

func (r *RedisClient) ListUserSessions(ctx context.Context, userID string) ([]string, error) {
	pattern := "session:*"
	iter := r.client.Scan(ctx, 0, pattern, 0).Iterator()
	
	var sessions []string
	for iter.Next(ctx) {
		key := iter.Val()
		data, err := r.client.HGetAll(ctx, key).Result()
		if err != nil {
			continue
		}
		if data["user_id"] == userID {
			sessions = append(sessions, key)
		}
	}
	
	return sessions, iter.Err()
}
