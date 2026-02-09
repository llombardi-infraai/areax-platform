import { Link } from 'react-router-dom'
import { ROUTES } from '../lib/constants'
import { Briefcase, Shield, MessageSquare, ArrowRight } from 'lucide-react'

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Welcome to Area X</h1>
        <p className="text-gray-600">
          Your AI-powered business operating system. Manage workspaces, analyze data, and get AI recommendations.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <QuickActionCard
          icon={Briefcase}
          title="Workspaces"
          description="Manage your workspaces and projects"
          link={ROUTES.WORKSPACES}
        />
        <QuickActionCard
          icon={Shield}
          title="Security"
          description="Review security settings and audit logs"
          link={ROUTES.SECURITY}
        />
        <QuickActionCard
          icon={MessageSquare}
          title="AI Advisor"
          description="Get AI-powered business recommendations"
          link={ROUTES.AI_CHAT}
        />
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
        <div className="text-gray-500 text-center py-8">
          No recent activity to display
        </div>
      </div>
    </div>
  )
}

function QuickActionCard({
  icon: Icon,
  title,
  description,
  link,
}: {
  icon: typeof Briefcase
  title: string
  description: string
  link: string
}) {
  return (
    <Link
      to={link}
      className="block bg-white rounded-lg border border-gray-200 p-6 hover:border-primary-500 hover:shadow-sm transition-all group"
    >
      <div className="flex items-start justify-between">
        <div className="p-3 bg-primary-50 rounded-lg">
          <Icon className="w-6 h-6 text-primary-600" />
        </div>
        <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-primary-600 transition-colors" />
      </div>
      <h3 className="font-semibold mt-4">{title}</h3>
      <p className="text-sm text-gray-600 mt-1">{description}</p>
    </Link>
  )
}
