import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { Workspace, Project } from '@/types'
import { useUIStore } from '@/stores/uiStore'

export function useWorkspaces() {
  return useQuery({
    queryKey: ['workspaces'],
    queryFn: async () => {
      const response = await api.getWorkspaces()
      return response.data as Workspace[]
    },
  })
}

export function useWorkspace(id: string | null) {
  return useQuery({
    queryKey: ['workspace', id],
    queryFn: async () => {
      if (!id) return null
      const response = await api.getWorkspace(id)
      return response.data as Workspace
    },
    enabled: !!id,
  })
}

export function useProjects(workspaceId: string | null) {
  return useQuery({
    queryKey: ['projects', workspaceId],
    queryFn: async () => {
      if (!workspaceId) return []
      const response = await api.getProjects(workspaceId)
      return response.data as Project[]
    },
    enabled: !!workspaceId,
  })
}

export function useProject(id: string | null) {
  return useQuery({
    queryKey: ['project', id],
    queryFn: async () => {
      if (!id) return null
      const response = await api.getProject(id)
      return response.data as Project
    },
    enabled: !!id,
  })
}

export function useTenantContext() {
  const { currentWorkspace, currentProject, setCurrentWorkspace, setCurrentProject } = useUIStore()
  const queryClient = useQueryClient()

  const switchWorkspace = (id: string | null) => {
    setCurrentWorkspace(id)
    setCurrentProject(null)
    // Pre-fetch projects for the new workspace
    if (id) {
      queryClient.prefetchQuery({
        queryKey: ['projects', id],
        queryFn: async () => {
          const response = await api.getProjects(id)
          return response.data as Project[]
        },
      })
    }
  }

  const switchProject = (id: string | null) => {
    setCurrentProject(id)
  }

  return {
    currentWorkspace,
    currentProject,
    switchWorkspace,
    switchProject,
  }
}