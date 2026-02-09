export interface Workspace {
  id: string
  name: string
  description?: string
  createdBy: string
  createdAt: string
  updatedAt: string
}

export interface Project {
  id: string
  workspaceId: string
  name: string
  description?: string
  createdBy: string
  createdAt: string
  updatedAt: string
}

export interface Document {
  id: string
  projectId: string
  type: 'blueprint' | 'knowledge_base' | 'checklist' | 'policy'
  title: string
  content: Record<string, any>
  privacy: 'project' | 'workspace' | 'org' | 'restricted'
  createdBy: string
  createdAt: string
  updatedAt: string
}
