import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { API_BASE, STORAGE_KEYS } from './constants'

// Create axios instances for different APIs
export const controlPlaneApi: AxiosInstance = axios.create({
  baseURL: API_BASE.controlPlane,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

export const tenantApi: AxiosInstance = axios.create({
  baseURL: API_BASE.tenantApi,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Request interceptor to add auth token
const addAuthToken = (config: AxiosRequestConfig): AxiosRequestConfig => {
  const token = localStorage.getItem(STORAGE_KEYS.TOKEN)
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}

controlPlaneApi.interceptors.request.use(addAuthToken as any)
tenantApi.interceptors.request.use(addAuthToken as any)

// Response interceptor for error handling
const handleResponseError = async (error: AxiosError) => {
  const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }

  if (error.response?.status === 401 && !originalRequest._retry) {
    originalRequest._retry = true
    
    try {
      const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN)
      if (!refreshToken) {
        throw new Error('No refresh token')
      }

      const response = await axios.post(`${API_BASE.controlPlane}/auth/refresh`, {
        refreshToken,
      })

      const { token, refreshToken: newRefreshToken } = response.data
      localStorage.setItem(STORAGE_KEYS.TOKEN, token)
      localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, newRefreshToken)

      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${token}`
      }
      return axios(originalRequest)
    } catch (refreshError) {
      // Clear auth data and redirect to login
      localStorage.removeItem(STORAGE_KEYS.TOKEN)
      localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN)
      localStorage.removeItem(STORAGE_KEYS.USER)
      window.location.href = '/login'
      return Promise.reject(refreshError)
    }
  }

  return Promise.reject(error)
}

controlPlaneApi.interceptors.response.use(
  (response: AxiosResponse) => response,
  handleResponseError
)

tenantApi.interceptors.response.use(
  (response: AxiosResponse) => response,
  handleResponseError
)

// API helper functions
export const api = {
  // Auth
  login: (email: string, password: string) =>
    controlPlaneApi.post('/auth/login', { email, password }),
  
  verifyMFA: (code: string, tempToken: string) =>
    controlPlaneApi.post('/auth/mfa/verify', { code, tempToken }),
  
  setupMFA: () =>
    controlPlaneApi.post('/auth/mfa/setup'),
  
  confirmMFA: (code: string, secret: string) =>
    controlPlaneApi.post('/auth/mfa/confirm', { code, secret }),
  
  forgotPassword: (email: string) =>
    controlPlaneApi.post('/auth/forgot-password', { email }),
  
  resetPassword: (token: string, password: string) =>
    controlPlaneApi.post('/auth/reset-password', { token, password }),
  
  logout: () =>
    controlPlaneApi.post('/auth/logout'),

  // User
  getCurrentUser: () =>
    controlPlaneApi.get('/users/me'),
  
  updateUser: (data: Partial<User>) =>
    controlPlaneApi.patch('/users/me', data),

  // Workspaces
  getWorkspaces: () =>
    tenantApi.get('/workspaces'),
  
  getWorkspace: (id: string) =>
    tenantApi.get(`/workspaces/${id}`),
  
  createWorkspace: (data: CreateWorkspaceData) =>
    tenantApi.post('/workspaces', data),
  
  updateWorkspace: (id: string, data: Partial<CreateWorkspaceData>) =>
    tenantApi.patch(`/workspaces/${id}`, data),
  
  deleteWorkspace: (id: string) =>
    tenantApi.delete(`/workspaces/${id}`),

  // Projects
  getProjects: (workspaceId: string) =>
    tenantApi.get(`/workspaces/${workspaceId}/projects`),
  
  getProject: (id: string) =>
    tenantApi.get(`/projects/${id}`),
  
  createProject: (workspaceId: string, data: CreateProjectData) =>
    tenantApi.post(`/workspaces/${workspaceId}/projects`, data),

  // Documents
  getDocuments: (projectId: string) =>
    tenantApi.get(`/projects/${projectId}/documents`),
  
  getDocument: (id: string) =>
    tenantApi.get(`/documents/${id}`),

  // AI
  sendChatMessage: (message: string, context?: string) =>
    tenantApi.post('/ai/chat', { message, context }),
  
  startBlueprint: (topic: string) =>
    tenantApi.post('/ai/blueprints/start', { topic }),
  
  answerBlueprint: (sessionId: string, answer: string) =>
    tenantApi.post(`/ai/blueprints/${sessionId}/answer`, { answer }),
  
  getBlueprints: () =>
    tenantApi.get('/blueprints'),
  
  getBlueprint: (id: string) =>
    tenantApi.get(`/blueprints/${id}`),

  // Security
  getSecurityOverview: () =>
    tenantApi.get('/security/overview'),
  
  getUsers: () =>
    controlPlaneApi.get('/users'),
  
  getSessions: () =>
    controlPlaneApi.get('/sessions'),
  
  revokeSession: (id: string) =>
    controlPlaneApi.delete(`/sessions/${id}`),
  
  getAuditLogs: (params?: { page?: number; limit?: number; from?: string; to?: string }) =>
    tenantApi.get('/audit-logs', { params }),

  // Data Control
  getRetentionPolicy: () =>
    tenantApi.get('/data/retention'),
  
  updateRetentionPolicy: (data: RetentionPolicy) =>
    tenantApi.patch('/data/retention', data),
  
  requestExport: (data: ExportRequest) =>
    tenantApi.post('/data/exports', data),
  
  getExports: () =>
    tenantApi.get('/data/exports'),
  
  requestDeletion: (data: DeletionRequest) =>
    tenantApi.post('/data/deletions', data),
  
  getDeletions: () =>
    tenantApi.get('/data/deletions'),

  // Knowledge Base
  getKnowledgeDocs: () =>
    tenantApi.get('/knowledge'),
  
  getKnowledgeDoc: (id: string) =>
    tenantApi.get(`/knowledge/${id}`),
  
  createKnowledgeDoc: (data: CreateKnowledgeDoc) =>
    tenantApi.post('/knowledge', data),
  
  updateKnowledgeDoc: (id: string, data: Partial<CreateKnowledgeDoc>) =>
    tenantApi.patch(`/knowledge/${id}`, data),

  // Connectors
  getConnectors: () =>
    tenantApi.get('/connectors'),
  
  installConnector: (id: string) =>
    tenantApi.post(`/connectors/${id}/install`),

  // Notifications
  getNotifications: () =>
    controlPlaneApi.get('/notifications'),
  
  markNotificationRead: (id: string) =>
    controlPlaneApi.patch(`/notifications/${id}/read`),
}

// Type definitions for API
interface User {
  id: string
  email: string
  name: string
  mfaEnabled: boolean
  role: string
}

interface CreateWorkspaceData {
  name: string
  description?: string
}

interface CreateProjectData {
  name: string
  description?: string
}

interface RetentionPolicy {
  documentRetentionDays: number
  auditLogRetentionDays: number
  autoDeleteEnabled: boolean
}

interface ExportRequest {
  dataTypes: string[]
  format: 'json' | 'csv'
}

interface DeletionRequest {
  dataType: string
  identifier: string
  reason: string
}

interface CreateKnowledgeDoc {
  title: string
  content: string
  tags?: string[]
}