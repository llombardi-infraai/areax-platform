import { useState } from 'react'
import { Shield, Users, Activity, FileText } from 'lucide-react'

export default function Security() {
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'audit'>('overview')

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Security Center</h1>
        <p className="text-gray-600">Monitor and manage your organization's security</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-gray-200">
        <TabButton
          active={activeTab === 'overview'}
          onClick={() => setActiveTab('overview')}
          icon={Shield}
          label="Overview"
        />
        <TabButton
          active={activeTab === 'users'}
          onClick={() => setActiveTab('users')}
          icon={Users}
          label="Users"
        />
        <TabButton
          active={activeTab === 'audit'}
          onClick={() => setActiveTab('audit')}
          icon={FileText}
          label="Audit Logs"
        />
      </div>

      {/* Content */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        {activeTab === 'overview' && <OverviewTab />}
        {activeTab === 'users' && <UsersTab />}
        {activeTab === 'audit' && <AuditTab />}
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
  icon: typeof Shield
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

function OverviewTab() {
  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-3 gap-4">
        <StatCard
          icon={Shield}
          label="MFA Adoption"
          value="0%"
          description="0 of 0 users enabled"
        />
        <StatCard
          icon={Activity}
          label="Active Sessions"
          value="0"
          description="Across all users"
        />
        <StatCard
          icon={FileText}
          label="Audit Events (24h)"
          value="0"
          description="Security-related events"
        />
      </div>

      <div>
        <h3 className="font-semibold mb-3">Security Recommendations</h3>
        <div className="space-y-2">
          <div className="flex items-center gap-3 p-3 bg-yellow-50 rounded-lg">
            <div className="w-2 h-2 bg-yellow-500 rounded-full" />
            <span className="text-sm">Enable MFA for all users</span>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({
  icon: Icon,
  label,
  value,
  description,
}: {
  icon: typeof Shield
  label: string
  value: string
  description: string
}) {
  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <div className="flex items-center gap-2 text-gray-600 mb-2">
        <Icon className="w-4 h-4" />
        <span className="text-sm">{label}</span>
      </div>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-sm text-gray-500">{description}</div>
    </div>
  )
}

function UsersTab() {
  return (
    <div>
      <h3 className="font-semibold mb-4">Users</h3>
      <div className="text-gray-500 text-center py-8">No users to display</div>
    </div>
  )
}

function AuditTab() {
  return (
    <div>
      <h3 className="font-semibold mb-4">Audit Logs</h3>
      <div className="text-gray-500 text-center py-8">No audit logs to display</div>
    </div>
  )
}
