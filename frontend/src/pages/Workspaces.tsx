import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Folder, MoreVertical } from 'lucide-react'
import { ROUTES } from '../lib/constants'
import type { Workspace } from '../types/workspace'

export default function Workspaces() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([])
  const [isLoading, setIsLoading] = useState(false)

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Workspaces</h1>
          <p className="text-gray-600">Manage your workspaces and projects</p>
        </div>
        <button className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700">
          <Plus className="w-5 h-5" />
          New Workspace
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : workspaces.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Folder className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium mb-2">No workspaces yet</h3>
          <p className="text-gray-600 mb-4">
            Create your first workspace to start organizing your projects
          </p>
          <button className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 mx-auto">
            <Plus className="w-5 h-5" />
            Create Workspace
          </button>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {workspaces.map((workspace) => (
            <WorkspaceCard key={workspace.id} workspace={workspace} />
          ))}
        </div>
      )}
    </div>
  )
}

function WorkspaceCard({ workspace }: { workspace: Workspace }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:border-primary-500 transition-colors">
      <div className="flex items-start justify-between">
        <Link
          to={ROUTES.WORKSPACE_DETAIL.replace(':id', workspace.id)}
          className="flex-1"
        >
          <h3 className="font-semibold text-lg">{workspace.name}</h3>
          {workspace.description && (
            <p className="text-gray-600 text-sm mt-1">{workspace.description}</p>
          )}
        </Link>
        <button className="p-2 hover:bg-gray-100 rounded-lg">
          <MoreVertical className="w-5 h-5 text-gray-400" />
        </button>
      </div>
    </div>
  )
}
