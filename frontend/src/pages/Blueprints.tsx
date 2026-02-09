import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, FileText, MoreVertical, CheckCircle } from 'lucide-react'
import { ROUTES } from '../lib/constants'
import type { Blueprint } from '../types/ai'

export default function Blueprints() {
  const [blueprints, setBlueprints] = useState<Blueprint[]>([])
  const [isLoading, setIsLoading] = useState(false)

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Blueprints</h1>
          <p className="text-gray-600">AI-generated business plans and recommendations</p>
        </div>
        <Link
          to={ROUTES.AI_BLUEPRINT}
          className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
        >
          <Plus className="w-5 h-5" />
          New Blueprint
        </Link>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : blueprints.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <FileText className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium mb-2">No blueprints yet</h3>
          <p className="text-gray-600 mb-4">
            Create your first blueprint to get AI-powered business recommendations
          </p>
          <Link
            to={ROUTES.AI_BLUEPRINT}
            className="inline-flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
          >
            <Plus className="w-5 h-5" />
            Create Blueprint
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {blueprints.map((blueprint) => (
            <BlueprintCard key={blueprint.id} blueprint={blueprint} />
          ))}
        </div>
      )}
    </div>
  )
}

function BlueprintCard({ blueprint }: { blueprint: Blueprint }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:border-primary-500 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="font-semibold text-lg">{blueprint.business.name}</h3>
          <p className="text-gray-600 text-sm mt-1">
            {blueprint.recommendations.length} recommendations
          </p>
          <div className="flex items-center gap-4 mt-3">
            <div className="flex items-center gap-1 text-sm text-gray-500">
              <CheckCircle className="w-4 h-4" />
              {blueprint.checklist.filter(i => i.completed).length} of {blueprint.checklist.length} tasks
            </div>
          </div>
        </div>
        <button className="p-2 hover:bg-gray-100 rounded-lg">
          <MoreVertical className="w-5 h-5 text-gray-400" />
        </button>
      </div>
    </div>
  )
}
