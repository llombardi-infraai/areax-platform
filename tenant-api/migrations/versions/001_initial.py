# Initial migration - Create all tables

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE workspace_status AS ENUM ('active', 'archived', 'suspended')")
    op.execute("CREATE TYPE project_status AS ENUM ('draft', 'active', 'completed', 'archived')")
    op.execute("CREATE TYPE project_type AS ENUM ('software', 'infrastructure', 'security', 'data', 'other')")
    op.execute("CREATE TYPE document_type AS ENUM ('blueprint', 'knowledge_base', 'requirement', 'architecture', 'design', 'policy', 'standard', 'other')")
    op.execute("CREATE TYPE document_status AS ENUM ('draft', 'review', 'approved', 'published', 'archived')")
    op.execute("CREATE TYPE conversation_status AS ENUM ('active', 'completed', 'archived')")
    op.execute("CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system')")
    op.execute("CREATE TYPE audit_action AS ENUM ('create', 'read', 'update', 'delete', 'export', 'login', 'logout', 'permission_denied', 'ai_query', 'ai_response')")
    op.execute("CREATE TYPE audit_severity AS ENUM ('info', 'warning', 'error', 'critical')")
    op.execute("CREATE TYPE notification_type AS ENUM ('info', 'warning', 'error', 'success', 'security', 'system')")
    op.execute("CREATE TYPE notification_priority AS ENUM ('low', 'normal', 'high', 'urgent')")
    op.execute("CREATE TYPE connector_type AS ENUM ('aws', 'azure', 'gcp', 'github', 'gitlab', 'jira', 'slack', 'teams', 'custom')")
    op.execute("CREATE TYPE connector_status AS ENUM ('pending', 'connected', 'error', 'disconnected')")
    op.execute("CREATE TYPE export_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'expired')")
    op.execute("CREATE TYPE export_format AS ENUM ('json', 'csv', 'pdf', 'zip')")
    op.execute("CREATE TYPE deletion_status AS ENUM ('pending', 'approved', 'rejected', 'processing', 'completed', 'failed')")
    
    # Workspaces
    op.create_table(
        'workspaces',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('org_id', sa.String(255), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('status', sa.Enum('active', 'archived', 'suspended', name='workspace_status'), default='active'),
        sa.Column('settings', postgresql.JSONB, default=dict),
        sa.Column('created_by', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_workspace_org_status', 'workspaces', ['org_id', 'status'])
    
    # Projects
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('org_id', sa.String(255), nullable=False, index=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('type', sa.Enum('software', 'infrastructure', 'security', 'data', 'other', name='project_type'), default='software'),
        sa.Column('status', sa.Enum('draft', 'active', 'completed', 'archived', name='project_status'), default='draft'),
        sa.Column('settings', postgresql.JSONB, default=dict),
        sa.Column('metadata', postgresql.JSONB, default=dict),
        sa.Column('created_by', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_project_org_workspace', 'projects', ['org_id', 'workspace_id'])
    op.create_index('idx_project_status', 'projects', ['org_id', 'status'])
    
    # Documents
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('org_id', sa.String(255), nullable=False, index=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.Enum('blueprint', 'knowledge_base', 'requirement', 'architecture', 'design', 'policy', 'standard', 'other', name='document_type'), default='other'),
        sa.Column('status', sa.Enum('draft', 'review', 'approved', 'published', 'archived', name='document_status'), default='draft'),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content', sa.Text),
        sa.Column('content_json', postgresql.JSONB),
        sa.Column('version', sa.String(50), default='1.0'),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='SET NULL')),
        sa.Column('created_by', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_document_org_project', 'documents', ['org_id', 'project_id'])
    op.create_index('idx_document_type', 'documents', ['org_id', 'type'])
    
    # AI Conversations
    op.create_table(
        'ai_conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('org_id', sa.String(255), nullable=False, index=True),
        sa.Column('user_id', sa.String(255), nullable=False, index=True),
        sa.Column('title', sa.String(255)),
        sa.Column('context', postgresql.JSONB, default=dict),
        sa.Column('status', sa.Enum('active', 'completed', 'archived', name='conversation_status'), default='active'),
        sa.Column('metadata', postgresql.JSONB, default=dict),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_conversation_org_user', 'ai_conversations', ['org_id', 'user_id'])
    
    # AI Messages
    op.create_table(
        'ai_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('org_id', sa.String(255), nullable=False, index=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.Enum('user', 'assistant', 'system', name='message_role'), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('tokens_used', sa.Integer, default=0),
        sa.Column('latency_ms', sa.Integer, default=0),
        sa.Column('metadata', postgresql.JSONB, default=dict),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    
    # AI Memories
    op.create_table(
        'ai_memories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('org_id', sa.String(255), nullable=False, index=True),
        sa.Column('user_id', sa.String(255), index=True),
        sa.Column('key', sa.String(255), nullable=False),
        sa.Column('value', sa.Text, nullable=False),
        sa.Column('source_conversation_id', postgresql.UUID(as_uuid=True)),
        sa.Column('confidence', sa.Float, default=1.0),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_memory_org_user', 'ai_memories', ['org_id', 'user_id'])
    op.create_index('idx_memory_key', 'ai_memories', ['org_id', 'key'])
    
    # Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('org_id', sa.String(255), nullable=False, index=True),
        sa.Column('user_id', sa.String(255)),
        sa.Column('action', sa.Enum('create', 'read', 'update', 'delete', 'export', 'login', 'logout', 'permission_denied', 'ai_query', 'ai_response', name='audit_action'), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', sa.String(255)),
        sa.Column('severity', sa.Enum('info', 'warning', 'error', 'critical', name='audit_severity'), default='info'),
        sa.Column('details', postgresql.JSONB, default=dict),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_audit_org_action', 'audit_logs', ['org_id', 'action'])
    op.create_index('idx_audit_created', 'audit_logs', ['created_at'])
    op.create_index('idx_audit_resource', 'audit_logs', ['org_id', 'resource_type', 'resource_id'])
    
    # Notifications
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('org_id', sa.String(255), nullable=False, index=True),
        sa.Column('user_id', sa.String(255), nullable=False, index=True),
        sa.Column('type', sa.Enum('info', 'warning', 'error', 'success', 'security', 'system', name='notification_type'), default='info'),
        sa.Column('priority', sa.Enum('low', 'normal', 'high', 'urgent', name='notification_priority'), default='normal'),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('data', postgresql.JSONB, default=dict),
        sa.Column('is_read', sa.Boolean, default=False),
        sa.Column('read_at', sa.DateTime(timezone=True)),
        sa.Column('action_url', sa.String(500)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
    )
    op.create_index('idx_notification_org_user', 'notifications', ['org_id', 'user_id'])
    op.create_index('idx_notification_unread', 'notifications', ['org_id', 'user_id', 'is_read'])
    op.create_index('idx_notification_created', 'notifications', ['created_at'])
    
    # Connectors
    op.create_table(
        'connectors',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('org_id', sa.String(255), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.Enum('aws', 'azure', 'gcp', 'github', 'gitlab', 'jira', 'slack', 'teams', 'custom', name='connector_type'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'connected', 'error', 'disconnected', name='connector_status'), default='pending'),
        sa.Column('config', postgresql.JSONB, default=dict),
        sa.Column('credentials_encrypted', sa.Text),
        sa.Column('last_tested_at', sa.DateTime(timezone=True)),
        sa.Column('last_error', sa.Text),
        sa.Column('created_by', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_connector_org', 'connectors', ['org_id'])
    op.create_index('idx_connector_type', 'connectors', ['org_id', 'type'])
    op.create_index('idx_connector_status', 'connectors', ['org_id', 'status'])
    
    # Exports
    op.create_table(
        'exports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('org_id', sa.String(255), nullable=False, index=True),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', 'expired', name='export_status'), default='pending'),
        sa.Column('format', sa.Enum('json', 'csv', 'pdf', 'zip', name='export_format'), default='json'),
        sa.Column('filters', postgresql.JSONB, default=dict),
        sa.Column('file_path', sa.String(500)),
        sa.Column('file_size', sa.Integer, default=0),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('error_message', sa.Text),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_export_org', 'exports', ['org_id'])
    op.create_index('idx_export_status', 'exports', ['org_id', 'status'])
    op.create_index('idx_export_user', 'exports', ['org_id', 'user_id'])
    
    # Deletion Requests
    op.create_table(
        'deletion_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('org_id', sa.String(255), nullable=False, index=True),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('requested_by', sa.String(255), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', sa.String(255), nullable=False),
        sa.Column('reason', sa.Text),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', 'processing', 'completed', 'failed', name='deletion_status'), default='pending'),
        sa.Column('approved_by', sa.String(255)),
        sa.Column('approved_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('error_message', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_deletion_org', 'deletion_requests', ['org_id'])
    op.create_index('idx_deletion_status', 'deletion_requests', ['org_id', 'status'])
    op.create_index('idx_deletion_resource', 'deletion_requests', ['org_id', 'resource_type', 'resource_id'])
    
    # Data Retention Policies
    op.create_table(
        'data_retention_policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('org_id', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('audit_logs_days', sa.Integer, default=365),
        sa.Column('conversation_history_days', sa.Integer, default=90),
        sa.Column('export_files_days', sa.Integer, default=30),
        sa.Column('soft_delete_days', sa.Integer, default=30),
        sa.Column('auto_purge_enabled', sa.Boolean, default=False),
        sa.Column('settings', postgresql.JSONB, default=dict),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_by', sa.String(255), nullable=False),
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('data_retention_policies')
    op.drop_table('deletion_requests')
    op.drop_table('exports')
    op.drop_table('connectors')
    op.drop_table('notifications')
    op.drop_table('audit_logs')
    op.drop_table('ai_memories')
    op.drop_table('ai_messages')
    op.drop_table('ai_conversations')
    op.drop_table('documents')
    op.drop_table('projects')
    op.drop_table('workspaces')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS deletion_status")
    op.execute("DROP TYPE IF EXISTS export_format")
    op.execute("DROP TYPE IF EXISTS export_status")
    op.execute("DROP TYPE IF EXISTS connector_status")
    op.execute("DROP TYPE IF EXISTS connector_type")
    op.execute("DROP TYPE IF EXISTS notification_priority")
    op.execute("DROP TYPE IF EXISTS notification_type")
    op.execute("DROP TYPE IF EXISTS audit_severity")
    op.execute("DROP TYPE IF EXISTS audit_action")
    op.execute("DROP TYPE IF EXISTS message_role")
    op.execute("DROP TYPE IF EXISTS conversation_status")
    op.execute("DROP TYPE IF EXISTS document_status")
    op.execute("DROP TYPE IF EXISTS document_type")
    op.execute("DROP TYPE IF EXISTS project_type")
    op.execute("DROP TYPE IF EXISTS project_status")
    op.execute("DROP TYPE IF EXISTS workspace_status")
