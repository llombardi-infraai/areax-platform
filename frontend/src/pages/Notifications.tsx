import { useState } from 'react'
import { Bell, Check, Trash2 } from 'lucide-react'

interface Notification {
  id: string
  type: 'security' | 'data' | 'platform' | 'ai'
  severity: 'info' | 'warning' | 'critical'
  title: string
  message: string
  isRead: boolean
  createdAt: string
}

export default function Notifications() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [filter, setFilter] = useState<'all' | 'unread'>('all')

  const unreadCount = notifications.filter((n) => !n.isRead).length

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Notifications</h1>
          <p className="text-gray-600">
            {unreadCount > 0
              ? `You have ${unreadCount} unread notification${unreadCount > 1 ? 's' : ''}`
              : 'No new notifications'}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg ${
              filter === 'all'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('unread')}
            className={`px-4 py-2 rounded-lg ${
              filter === 'unread'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Unread
          </button>
        </div>
      </div>

      {notifications.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Bell className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium mb-2">No notifications</h3>
          <p className="text-gray-600">
            You're all caught up! New notifications will appear here.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {notifications
            .filter((n) => (filter === 'unread' ? !n.isRead : true))
            .map((notification) => (
              <NotificationItem key={notification.id} notification={notification} />
            ))}
        </div>
      )}
    </div>
  )
}

function NotificationItem({ notification }: { notification: Notification }) {
  const severityColors = {
    info: 'bg-blue-50 border-blue-200',
    warning: 'bg-yellow-50 border-yellow-200',
    critical: 'bg-red-50 border-red-200',
  }

  return (
    <div
      className={`p-4 rounded-lg border ${severityColors[notification.severity]} ${
        !notification.isRead ? 'bg-opacity-100' : 'bg-opacity-50'
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            {!notification.isRead && (
              <span className="w-2 h-2 bg-primary-600 rounded-full"></span>
            )}
            <span className="text-xs uppercase tracking-wider text-gray-500">
              {notification.type}
            </span>
          </div>
          <h4 className="font-medium">{notification.title}</h4>
          <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
          <p className="text-xs text-gray-500 mt-2">
            {new Date(notification.createdAt).toLocaleString()}
          </p>
        </div>
        <div className="flex gap-1">
          {!notification.isRead && (
            <button className="p-2 hover:bg-white/50 rounded-lg" title="Mark as read">
              <Check className="w-4 h-4 text-gray-500" />
            </button>
          )}
          <button className="p-2 hover:bg-white/50 rounded-lg" title="Delete">
            <Trash2 className="w-4 h-4 text-gray-500" />
          </button>
        </div>
      </div>
    </div>
  )
}
