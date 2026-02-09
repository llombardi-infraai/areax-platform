export const API_BASE = {
  controlPlane: import.meta.env.VITE_CONTROL_API_URL || 'http://localhost:8080/v1',
  tenantApi: import.meta.env.VITE_TENANT_API_URL || 'http://localhost:8081/v1',
}

export const APP_NAME = 'Area X'

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  MFA_SETUP: '/mfa-setup',
  FORGOT_PASSWORD: '/forgot-password',
  WORKSPACES: '/workspaces',
  WORKSPACE_DETAIL: '/workspaces/:id',
  PROJECTS: '/projects/:id',
  AI_CHAT: '/ai/chat',
  AI_BLUEPRINT: '/ai/blueprint',
  BLUEPRINTS: '/blueprints',
  SECURITY: '/security',
  SECURITY_USERS: '/security/users',
  SECURITY_SESSIONS: '/security/sessions',
  SECURITY_AUDIT: '/security/audit-logs',
  DATA_RETENTION: '/data/retention',
  DATA_EXPORTS: '/data/exports',
  DATA_DELETIONS: '/data/deletions',
  KNOWLEDGE: '/knowledge',
  KNOWLEDGE_DETAIL: '/knowledge/:id',
  CONNECTORS: '/connectors',
  NOTIFICATIONS: '/notifications',
} as const

export const STORAGE_KEYS = {
  TOKEN: 'areax_token',
  REFRESH_TOKEN: 'areax_refresh_token',
  USER: 'areax_user',
  TENANT: 'areax_tenant',
}