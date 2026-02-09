package db

import (
	"time"
)

type User struct {
	ID            string     `json:"id"`
	Email         string     `json:"email"`
	PasswordHash  string     `json:"-"`
	MFASecret     *string    `json:"-"`
	MFAEnabled    bool       `json:"mfa_enabled"`
	RecoveryCodes []string   `json:"-"`
	CreatedAt     time.Time  `json:"created_at"`
}

type Organization struct {
	ID             string    `json:"id"`
	Name           string    `json:"name"`
	Slug           string    `json:"slug"`
	Region         string    `json:"region"`
	DatabaseHost   string    `json:"-"`
	DatabaseName   string    `json:"-"`
	StorageBucket  string    `json:"-"`
	CreatedAt      time.Time `json:"created_at"`
}

type OrganizationRouting struct {
	DatabaseHost  string `json:"database_host"`
	DatabaseName  string `json:"database_name"`
	StorageBucket string `json:"storage_bucket"`
	Region        string `json:"region"`
}

type Membership struct {
	ID        string    `json:"id"`
	UserID    string    `json:"user_id"`
	OrgID     string    `json:"org_id"`
	Role      string    `json:"role"`
	CreatedAt time.Time `json:"created_at"`
}

type Session struct {
	ID        string    `json:"id"`
	UserID    string    `json:"user_id"`
	OrgID     *string   `json:"org_id,omitempty"`
	TokenHash string    `json:"-"`
	ExpiresAt time.Time `json:"expires_at"`
	CreatedAt time.Time `json:"created_at"`
}

type SessionInfo struct {
	ID        string     `json:"id"`
	UserID    string     `json:"user_id"`
	OrgID     *string    `json:"org_id,omitempty"`
	CreatedAt time.Time  `json:"created_at"`
	ExpiresAt time.Time  `json:"expires_at"`
}
