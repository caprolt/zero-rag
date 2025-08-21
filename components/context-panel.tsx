"use client"

import { FileText, X, RefreshCw, AlertCircle, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { useDocumentContext } from "./context-provider"
import { useToast } from "@/hooks/use-toast"

export function ContextPanel() {
  const { selectedDocuments, contextSummary, isContextLoading, toggleDocument, clearContext, refreshContext } =
    useDocumentContext()
  const { toast } = useToast()

  const handleClearContext = () => {
    clearContext()
    toast({
      title: "Context cleared",
      description: "All documents removed from context",
    })
  }

  const handleRefreshContext = () => {
    refreshContext()
    toast({
      title: "Context refreshed",
      description: "Document context has been updated",
    })
  }

  if (selectedDocuments.length === 0) {
    return (
      <Card className="p-4 bg-muted/30 border-dashed transition-all duration-300 hover:bg-muted/40">
        <div className="flex items-center gap-2 text-muted-foreground">
          <AlertCircle className="h-4 w-4" />
          <span className="text-sm">No documents selected for context</span>
        </div>
        <p className="text-xs text-muted-foreground mt-1">
          Select documents from the sidebar to provide context for your conversations.
        </p>
      </Card>
    )
  }

  return (
    <Card className="p-4 bg-gradient-to-r from-primary/5 to-secondary/5 border-primary/20 transition-all duration-300 hover:shadow-md">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 bg-primary rounded-full animate-pulse" />
          <Sparkles className="h-4 w-4 text-primary" />
          <span className="text-sm font-medium">Active Context</span>
          <Badge variant="secondary" className="text-xs animate-in fade-in-0 slide-in-from-right-2">
            {selectedDocuments.length} docs
          </Badge>
        </div>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRefreshContext}
            disabled={isContextLoading}
            className="h-6 w-6 p-0 hover:bg-primary/10 transition-all duration-200"
          >
            <RefreshCw
              className={`h-3 w-3 transition-transform duration-500 ${isContextLoading ? "animate-spin" : "hover:rotate-180"}`}
            />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClearContext}
            className="h-6 w-6 p-0 hover:bg-destructive/10 hover:text-destructive transition-all duration-200"
          >
            <X className="h-3 w-3" />
          </Button>
        </div>
      </div>

      <ScrollArea className="max-h-32">
        <div className="space-y-2">
          {selectedDocuments.map((doc, index) => (
            <div
              key={doc.id}
              className="animate-in fade-in-0 slide-in-from-left-2"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="flex items-center gap-2 group">
                <FileText className="h-3 w-3 text-primary flex-shrink-0" />
                <span className="text-xs font-medium truncate group-hover:text-primary transition-colors">
                  {doc.name}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => toggleDocument(doc.id)}
                  className="h-4 w-4 p-0 ml-auto opacity-0 group-hover:opacity-100 transition-all duration-200 hover:bg-destructive/10 hover:text-destructive"
                >
                  <X className="h-2 w-2" />
                </Button>
              </div>
              {doc.summary && (
                <p className="text-xs text-muted-foreground mt-1 ml-5 opacity-80 group-hover:opacity-100 transition-opacity">
                  {doc.summary}
                </p>
              )}
              {index < selectedDocuments.length - 1 && <Separator className="mt-2" />}
            </div>
          ))}
        </div>
      </ScrollArea>
    </Card>
  )
}
