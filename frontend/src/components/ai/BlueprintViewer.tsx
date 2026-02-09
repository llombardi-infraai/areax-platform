import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tabs"
import type { Blueprint } from "@/types"
import { FileText, Download, Share2, CheckCircle, Clock, AlertCircle } from "lucide-react"
import { cn } from "@/lib/utils"

interface BlueprintViewerProps {
  blueprint: Blueprint
}

export function BlueprintViewer({ blueprint }: BlueprintViewerProps) {
  const [activeTab, setActiveTab] = useState("content")

  const getStatusIcon = (status: Blueprint["status"]) => {
    switch (status) {
      case "approved":
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case "in_review":
        return <Clock className="h-5 w-5 text-yellow-500" />
      case "archived":
        return <AlertCircle className="h-5 w-5 text-gray-500" />
      default:
        return <FileText className="h-5 w-5 text-blue-500" />
    }
  }

  const getStatusLabel = (status: Blueprint["status"]) => {
    switch (status) {
      case "approved":
        return "Approved"
      case "in_review":
        return "In Review"
      case "archived":
        return "Archived"
      default:
        return "Draft"
    }
  }

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2">
                {getStatusIcon(blueprint.status)}
                <CardTitle>{blueprint.title}</CardTitle>
              </div>
              <CardDescription className="mt-2">
                {blueprint.description}
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                <Share2 className="mr-2 h-4 w-4" />
                Share
              </Button>
              <Button variant="outline" size="sm">
                <Download className="mr-2 h-4 w-4" />
                Export
              </Button>
            </div>
          </div>
          <div className="flex items-center gap-4 mt-4 text-sm text-muted-foreground">
            <span className={cn(
              "px-2 py-1 rounded-full text-xs font-medium",
              blueprint.status === "approved" && "bg-green-100 text-green-700",
              blueprint.status === "in_review" && "bg-yellow-100 text-yellow-700",
              blueprint.status === "draft" && "bg-blue-100 text-blue-700",
              blueprint.status === "archived" && "bg-gray-100 text-gray-700"
            )}>
              {getStatusLabel(blueprint.status)}
            </span>
            <span>Created: {new Date(blueprint.createdAt).toLocaleDateString()}</span>
            <span>Updated: {new Date(blueprint.updatedAt).toLocaleDateString()}</span>
          </div>
        </CardHeader>
      </Card>

      {/* Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="content">Content</TabsTrigger>
          <TabsTrigger value="history">Version History</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>
        
        <TabsContent value="content" className="space-y-4">
          {blueprint.sections.map((section, index) => (
            <Card key={section.id}>
              <CardHeader>
                <CardTitle className="text-lg">
                  {index + 1}. {section.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose prose-sm max-w-none">
                  {section.content.split('\n').map((paragraph, i) => (
                    <p key={i} className="mb-4">{paragraph}</p>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle>Version History</CardTitle>
              <CardDescription>
                Track changes and previous versions of this blueprint
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Version history coming soon...</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings">
          <Card>
            <CardHeader>
              <CardTitle>Blueprint Settings</CardTitle>
              <CardDescription>
                Manage access, notifications, and other settings
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Settings coming soon...</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}