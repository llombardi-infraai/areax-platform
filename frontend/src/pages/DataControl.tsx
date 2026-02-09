import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Database, Download, Trash2, Clock, ChevronRight } from 'lucide-react'
import { ROUTES } from '../lib/constants'

export default function DataControl() {
  const [activeTab, setActiveTab] = useState<'retention' | 'exports' | 'deletions'>('retention')

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Data Control Center</h1>
        <p className="text-gray-600">Manage data retention, exports, and deletions</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-gray-200">
        <TabButton
          active={activeTab === 'retention'}
          onClick={() => setActiveTab('retention')}
          icon={Clock}
          label="Retention"
        />
        <TabButton
          active={activeTab === 'exports'}
          onClick={() => setActiveTab('exports')}
          icon={Download}
          label="Exports"
        />
        <TabButton
          active={activeTab === 'deletions'}
          onClick={() => setActiveTab('deletions')}
          icon={Trash2}
          label="Deletions"
        />
      </div>

      {/* Content */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        {activeTab === 'retention' && <RetentionTab />}
        {activeTab === 'exports' && <ExportsTab />}
        {activeTab === 'deletions' && <DeletionsTab />}
      </div>
    </div>
  )
}

function TabButton({
  active,
  onClick,
  icon: Icon,
  label,
}: {
  active: boolean
  onClick: () => void
  icon: typeof Database
  label: string
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
        active
          ? 'border-primary-600 text-primary-600'
          : 'border-transparent text-gray-600 hover:text-gray-900'
      }`}
    >
      <Icon className="w-4 h-4" />
      {label}
    </button>
  )
}

function RetentionTab() {
  const settings = [
    { type: 'AI Chat Logs', days: 90, description: 'Conversations with AI advisor' },
    { type: 'AI Summaries', days: 365, description: 'Generated summaries and insights' },
    { type: 'Audit Logs', days: 2555, description: 'Security and action logs (7 years)' },
    { type: 'Notifications', days: 365, description: 'User notifications' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h3 className="font-semibold mb-4">Retention Settings</h3>
        <div className="space-y-3">
          {settings.map((setting) => (
            <div
              key={setting.type}
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
            >
              <div>
                <h4 className="font-medium">{setting.type}</h4>
                <p className="text-sm text-gray-600">{setting.description}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-primary-600">{setting.days}</span>
                <span className="text-gray-500">days</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-yellow-50 p-4 rounded-lg">
        <p className="text-sm text-yellow-800">
          <strong>Note:</strong> Changing retention settings will only affect new data. 
          Existing data will follow the previous retention schedule.
        </p>
      </div>
    </div>
  )
}

function ExportsTab() {
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">Data Exports</h3>
        <button className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700">
          <Download className="w-4 h-4" />
          Request Export
        </button>
      </div>

      <div className="text-gray-500 text-center py-8">
        No exports available
      </div>

      <div className="bg-gray-50 p-4 rounded-lg mt-4">
        <h4 className="font-medium mb-2">About Data Exports</h4>
        <ul className="text-sm text-gray-600 space-y-1 list-disc list-inside">
          <li>Exports include all data for your organization</li>
          <li>Data is provided in JSON format</li>
          <li>Export links expire after 72 hours</li>
          <li>Only organization owners can request exports</li>
        </ul>
      </div>
    </div>
  )
}

function DeletionsTab() {
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">Deletion Requests</h3>
        <button className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700">
          <Trash2 className="w-4 h-4" />
          Request Deletion
        </button>
      </div>

      <div className="text-gray-500 text-center py-8">
        No deletion requests
      </div>

      <div className="bg-red-50 p-4 rounded-lg mt-4">
        <h4 className="font-medium text-red-800 mb-2">⚠️ Warning</h4>
        <p className="text-sm text-red-700">
          Data deletion is permanent and cannot be undone. Deletion requests require 
          approval from a second administrator and may take up to 30 days to process.
        </p>
      </div>
    </div>
  )
}
