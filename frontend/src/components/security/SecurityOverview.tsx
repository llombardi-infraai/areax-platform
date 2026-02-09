import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card"
import { Shield, Users, Key, FileText } from "lucide-react"

export function SecurityOverview() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Security Center</h1>
        <p className="text-muted-foreground">
          Monitor and manage your organization&apos;s security posture
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">42</div>
            <p className="text-xs text-muted-foreground">+2 this month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">MFA Adoption</CardTitle>
            <Key className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">87%</div>
            <p className="text-xs text-muted-foreground">37 of 42 users</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground">Across 8 users</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Audit Events</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,284</div>
            <p className="text-xs text-muted-foreground">Last 30 days</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Security Recommendations</CardTitle>
            <CardDescription>
              Actions to improve your security posture
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              <li className="flex items-start gap-2">
                <div className="rounded-full bg-yellow-100 p-1">
                  <Shield className="h-3 w-3 text-yellow-600" />
                </div>
                <div>
                  <p className="text-sm font-medium">Enable mandatory MFA</p>
                  <p className="text-xs text-muted-foreground">5 users don&apos;t have MFA enabled</p>
                </div>
              </li>
              <li className="flex items-start gap-2">
                <div className="rounded-full bg-green-100 p-1">
                  <Shield className="h-3 w-3 text-green-600" />
                </div>
                <div>
                  <p className="text-sm font-medium">Review inactive users</p>
                  <p className="text-xs text-muted-foreground">3 users haven&apos;t logged in for 90+ days</p>
                </div>
              </li>
              <li className="flex items-start gap-2">
                <div className="rounded-full bg-blue-100 p-1">
                  <Shield className="h-3 w-3 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm font-medium">Update session timeout</p>
                  <p className="text-xs text-muted-foreground">Current: 24 hours, Recommended: 8 hours</p>
                </div>
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Security Events</CardTitle>
            <CardDescription>
              Latest security-related activities
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              <li className="text-sm">
                <span className="font-medium">MFA enabled</span>
                <span className="text-muted-foreground"> by </span>
                <span>john@example.com</span>
                <span className="text-xs text-muted-foreground block">2 hours ago</span>
              </li>
              <li className="text-sm">
                <span className="font-medium">Failed login attempt</span>
                <span className="text-muted-foreground"> from IP </span>
                <span>192.168.1.100</span>
                <span className="text-xs text-muted-foreground block">5 hours ago</span>
              </li>
              <li className="text-sm">
                <span className="font-medium">Password changed</span>
                <span className="text-muted-foreground"> by </span>
                <span>jane@example.com</span>
                <span className="text-xs text-muted-foreground block">1 day ago</span>
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}