import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table"
import type { Session } from "@/types"
import { Monitor, Smartphone, LogOut } from "lucide-react"

// Mock data - would come from API
const mockSessions: Session[] = [
  {
    id: "1",
    userId: "1",
    userAgent: "Chrome on macOS",
    ipAddress: "192.168.1.50",
    createdAt: "2024-02-09T10:00:00Z",
    expiresAt: "2024-02-10T10:00:00Z",
    isCurrent: true,
  },
  {
    id: "2",
    userId: "1",
    userAgent: "Safari on iPhone",
    ipAddress: "192.168.1.51",
    createdAt: "2024-02-09T08:00:00Z",
    expiresAt: "2024-02-10T08:00:00Z",
    isCurrent: false,
  },
  {
    id: "3",
    userId: "2",
    userAgent: "Firefox on Windows",
    ipAddress: "192.168.1.52",
    createdAt: "2024-02-08T14:00:00Z",
    expiresAt: "2024-02-09T14:00:00Z",
    isCurrent: false,
  },
]

export function SessionsList() {
  const handleRevoke = (sessionId: string) => {
    // TODO: Implement revoke session
    console.log("Revoke session:", sessionId)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Active Sessions</h1>
        <p className="text-muted-foreground">
          Manage active user sessions across your organization
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Sessions</CardTitle>
          <CardDescription>
            {mockSessions.length} active sessions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Device</TableHead>
                <TableHead>IP Address</TableHead>
                <TableHead>Started</TableHead>
                <TableHead>Expires</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="w-24"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {mockSessions.map((session) => (
                <TableRow key={session.id}>
                  <TableCell className="flex items-center gap-2">
                    {session.userAgent?.includes("iPhone") || session.userAgent?.includes("Android") ? (
                      <Smartphone className="h-4 w-4 text-muted-foreground" />
                    ) : (
                      <Monitor className="h-4 w-4 text-muted-foreground" />
                    )}
                    <span className="text-sm">{session.userAgent}</span>
                  </TableCell>
                  <TableCell>{session.ipAddress}</TableCell>
                  <TableCell>{new Date(session.createdAt).toLocaleString()}</TableCell>
                  <TableCell>{new Date(session.expiresAt).toLocaleString()}</TableCell>
                  <TableCell>
                    {session.isCurrent ? (
                      <Badge variant="default">Current</Badge>
                    ) : (
                      <Badge variant="secondary">Active</Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    {!session.isCurrent && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRevoke(session.id)}
                      >
                        <LogOut className="h-4 w-4 mr-1" />
                        Revoke
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}