import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card"
import { Input } from "@/components/ui/Input"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table"
import type { AuditLog } from "@/types"
import { Search, Filter, Download } from "lucide-react"
import { useState } from "react"

// Mock data - would come from API
const mockAuditLogs: AuditLog[] = [
  {
    id: "1",
    action: "user.login",
    actorId: "1",
    actorEmail: "admin@example.com",
    resourceType: "session",
    resourceId: "sess_123",
    details: { ip: "192.168.1.50" },
    ipAddress: "192.168.1.50",
    createdAt: "2024-02-09T10:00:00Z",
  },
  {
    id: "2",
    action: "document.created",
    actorId: "2",
    actorEmail: "john@example.com",
    resourceType: "document",
    resourceId: "doc_456",
    details: { title: "AI Policy Draft" },
    ipAddress: "192.168.1.51",
    createdAt: "2024-02-09T09:30:00Z",
  },
  {
    id: "3",
    action: "blueprint.updated",
    actorId: "1",
    actorEmail: "admin@example.com",
    resourceType: "blueprint",
    resourceId: "bp_789",
    details: { changes: ["title", "content"] },
    ipAddress: "192.168.1.50",
    createdAt: "2024-02-09T09:00:00Z",
  },
]

const getActionColor = (action: string) => {
  if (action.includes("login") || action.includes("auth")) return "default"
  if (action.includes("create")) return "secondary"
  if (action.includes("update") || action.includes("edit")) return "outline"
  if (action.includes("delete")) return "destructive"
  return "default"
}

export function AuditLogViewer() {
  const [search, setSearch] = useState("")
  const [dateFrom, setDateFrom] = useState("")
  const [dateTo, setDateTo] = useState("")

  const filteredLogs = mockAuditLogs.filter(log =>
    log.action.toLowerCase().includes(search.toLowerCase()) ||
    log.actorEmail.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Audit Logs</h1>
        <p className="text-muted-foreground">
          Review all activity across your organization
        </p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <CardTitle>Activity Log</CardTitle>
              <CardDescription>
                Track changes and access across the platform
              </CardDescription>
            </div>
            <div className="flex flex-wrap gap-2">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search logs..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-8 w-48"
                />
              </div>
              <Input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="w-36"
              />
              <Input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="w-36"
              />
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filter
              </Button>
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Timestamp</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>Actor</TableHead>
                <TableHead>Resource</TableHead>
                <TableHead>IP Address</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredLogs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell className="font-mono text-sm">
                    {new Date(log.createdAt).toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <Badge variant={getActionColor(log.action)}>
                      {log.action}
                    </Badge>
                  </TableCell>
                  <TableCell>{log.actorEmail}</TableCell>
                  <TableCell>
                    {log.resourceType}
                    {log.resourceId && (
                      <span className="text-muted-foreground text-sm block">
                        {log.resourceId}
                      </span>
                    )}
                  </TableCell>
                  <TableCell className="font-mono text-sm">{log.ipAddress}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}