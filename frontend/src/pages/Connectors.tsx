import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Puzzle, ExternalLink, Check, Plus } from 'lucide-react'
import { ROUTES } from '../lib/constants'

interface Connector {
  id: string
  name: string
  description: string
  icon: string
  status: 'connected' | 'disconnected' | 'error'
}

const availableConnectors: Connector[] = [
  {
    id: 'ghl',
    name: 'GoHighLevel',
    description: 'CRM and marketing automation platform',
    icon: '📊',
    status: 'disconnected',
  },
  {
    id: 'metabase',
    name: 'Metabase',
    description: 'Business intelligence and analytics',
    icon: '📈',
    status: 'disconnected',
  },
  {
    id: 'slack',
    name: 'Slack',
    description: 'Team messaging and collaboration',
    icon: '💬',
    status: 'disconnected',
  },
  {
    id: 'notion',
    name: 'Notion',
    description: 'Workspace and documentation',
    icon: '📝',
    status: 'disconnected',
  },
]

export default function Connectors() {
  const [connectors, setConnectors] = useState<Connector[]>(availableConnectors)

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Connectors</h1>
        <p className="text-gray-600">Integrate with external tools and services</p>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {connectors.map((connector) => (
          <ConnectorCard key={connector.id} connector={connector} />
        ))}
      </div>

      <div className="mt-8 bg-gray-50 rounded-lg p-6">
        <h3 className="font-semibold mb-2">About Connectors</h3>
        <p className="text-gray-600 text-sm">
          Connectors allow you to integrate Area X with your existing tools. 
          Data is synced securely and you maintain full control over what gets shared.
        </p>
      </div>
    </div>
  )
}

function ConnectorCard({ connector }: { connector: Connector }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:border-primary-500 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <span className="text-2xl">{connector.icon}</span>
          <div>
            <h3 className="font-semibold">{connector.name}</h3>
            <p className="text-sm text-gray-600">{connector.description}</p>
          </div>
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <span
          className={`text-sm ${
            connector.status === 'connected'
              ? 'text-green-600'
              : connector.status === 'error'
              ? 'text-red-600'
              : 'text-gray-500'
          }`}
        >
          {connector.status === 'connected' && (
            <span className="flex items-center gap-1">
              <Check className="w-4 h-4" /> Connected
            </span>
          )}
          {connector.status === 'disconnected' && 'Not connected'}
          {connector.status === 'error' && 'Connection error'}
        </span>

        <button
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm ${
            connector.status === 'connected'
              ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              : 'bg-primary-600 text-white hover:bg-primary-700'
          }`}
        >
          {connector.status === 'connected' ? (
            <>
              <ExternalLink className="w-4 h-4" />
              Manage
            </>
          ) : (
            <>
              <Plus className="w-4 h-4" />
              Connect
            </>
          )}
        </button>
      </div>
    </div>
  )
}
