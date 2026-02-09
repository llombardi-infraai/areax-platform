package db

import (
	"database/sql"
	"fmt"
)

func RunMigrations(db *sql.DB) error {
	migrations := []struct {
		name string
		sql  string
	}{
		{
			name: "create_users_table",
			sql: `CREATE TABLE IF NOT EXISTS users (
				id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
				email VARCHAR(255) UNIQUE NOT NULL,
				password_hash VARCHAR(255) NOT NULL,
				mfa_secret VARCHAR(255),
				mfa_enabled BOOLEAN DEFAULT FALSE,
				recovery_codes TEXT[],
				created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
			);`,
		},
		{
			name: "create_organizations_table",
			sql: `CREATE TABLE IF NOT EXISTS organizations (
				id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
				name VARCHAR(255) NOT NULL,
				slug VARCHAR(255) UNIQUE NOT NULL,
				region VARCHAR(50) NOT NULL,
				database_host VARCHAR(255) NOT NULL,
				database_name VARCHAR(255) NOT NULL,
				storage_bucket VARCHAR(255) NOT NULL,
				created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
			);`,
		},
		{
			name: "create_memberships_table",
			sql: `CREATE TABLE IF NOT EXISTS memberships (
				id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
				user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
				org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
				role VARCHAR(50) NOT NULL DEFAULT 'member',
				created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
				UNIQUE(user_id, org_id)
			);`,
		},
		{
			name: "create_sessions_table",
			sql: `CREATE TABLE IF NOT EXISTS sessions (
				id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
				user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
				org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
				token_hash VARCHAR(255) UNIQUE NOT NULL,
				expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
				created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
			);`,
		},
		{
			name: "create_sessions_indexes",
			sql: `CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
			CREATE INDEX IF NOT EXISTS idx_sessions_token_hash ON sessions(token_hash);
			CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);`,
		},
		{
			name: "create_users_email_index",
			sql: `CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);`,
		},
	}

	// Create migrations tracking table
	if _, err := db.Exec(`CREATE TABLE IF NOT EXISTS schema_migrations (
		name VARCHAR(255) PRIMARY KEY,
		applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
	);`); err != nil {
		return fmt.Errorf("failed to create migrations table: %w", err)
	}

	for _, migration := range migrations {
		var exists bool
		err := db.QueryRow("SELECT EXISTS(SELECT 1 FROM schema_migrations WHERE name = $1)", migration.name).Scan(&exists)
		if err != nil {
			return fmt.Errorf("failed to check migration %s: %w", migration.name, err)
		}

		if exists {
			continue
		}

		if _, err := db.Exec(migration.sql); err != nil {
			return fmt.Errorf("failed to run migration %s: %w", migration.name, err)
		}

		if _, err := db.Exec("INSERT INTO schema_migrations (name) VALUES ($1)", migration.name); err != nil {
			return fmt.Errorf("failed to record migration %s: %w", migration.name, err)
		}
	}

	return nil
}
