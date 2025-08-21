"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { FileText, Upload, Folder, Search, MoreVertical, Download, Trash2, Eye, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Input } from "@/components/ui/input"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"
import { useDocumentContext } from "./context-provider"
import { useToast } from "@/hooks/use-toast"

const folders = ["All Documents", "Projects", "Research", "Documentation", "Notes"]

export function DocumentSidebar() {
  const { documents, selectedDocuments, toggleDocument, uploadDocuments } = useDocumentContext()
  const { toast } = useToast()
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedFolder, setSelectedFolder] = useState("All Documents")
  const [isDragOver, setIsDragOver] = useState(false)

  const selectedCount = selectedDocuments.length

  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch = doc.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFolder = selectedFolder === "All Documents" || doc.folder === selectedFolder
    return matchesSearch && matchesFolder
  })

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragOver(false)

      const files = Array.from(e.dataTransfer.files)
      if (files.length > 0) {
        try {
          await uploadDocuments(files)
          toast({
            title: "Files uploaded",
            description: `${files.length} file(s) uploaded successfully`,
          })
        } catch (error) {
          toast({
            title: "Upload failed",
            description: "Failed to upload files. Please try again.",
            variant: "destructive",
          })
        }
      }
    },
    [toast],
  )

  const handleDocumentToggle = (id: string) => {
    const doc = documents.find((d) => d.id === id)
    if (doc) {
      toggleDocument(id)
      toast({
        title: doc.selected ? "Document removed from context" : "Document added to context",
        description: doc.name,
      })
    }
  }

  const getFileIcon = (type: string) => {
    const iconClass = "h-4 w-4 transition-colors"
    switch (type) {
      case "pdf":
        return <FileText className={`${iconClass} text-red-500`} />
      case "docx":
        return <FileText className={`${iconClass} text-blue-500`} />
      case "md":
        return <FileText className={`${iconClass} text-green-500`} />
      case "txt":
        return <FileText className={`${iconClass} text-gray-500`} />
      default:
        return <FileText className={`${iconClass} text-muted-foreground`} />
    }
  }

  return (
    <div className="w-80 border-r border-sidebar-border bg-sidebar flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-sidebar-border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-serif font-semibold text-sidebar-foreground">Documents</h2>
          <Button size="sm" className="bg-primary hover:bg-primary/90 transition-all duration-200 hover:scale-105">
            <Upload className="h-4 w-4 mr-2" />
            Upload
          </Button>
        </div>

        <div className="mb-3">
          <div className="flex items-center gap-2">
            <div
              className={`h-2 w-2 rounded-full transition-all duration-300 ${selectedCount > 0 ? "bg-primary animate-pulse" : "bg-muted"}`}
            />
            <span className="text-sm text-muted-foreground">
              {selectedCount > 0 ? `${selectedCount} documents in context` : "No context selected"}
            </span>
          </div>
        </div>

        {/* Search */}
        <div className="relative group">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground transition-colors group-focus-within:text-primary" />
          <Input
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-background/50 border-sidebar-border transition-all duration-200 focus-visible:bg-background"
          />
        </div>
      </div>

      {/* Folders */}
      <div className="p-4 border-b border-sidebar-border">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-sidebar-foreground">Folders</h3>
          <Button variant="ghost" size="sm" className="h-6 w-6 p-0 hover:bg-sidebar-accent/50">
            <Plus className="h-3 w-3" />
          </Button>
        </div>
        <div className="space-y-1">
          {folders.map((folder) => (
            <Button
              key={folder}
              variant={selectedFolder === folder ? "secondary" : "ghost"}
              size="sm"
              className={`w-full justify-start text-left transition-all duration-200 ${
                selectedFolder === folder
                  ? "bg-sidebar-accent text-sidebar-accent-foreground shadow-sm"
                  : "text-sidebar-foreground hover:bg-sidebar-accent/50 hover:translate-x-1"
              }`}
              onClick={() => setSelectedFolder(folder)}
            >
              <Folder className="h-4 w-4 mr-2" />
              {folder}
              <Badge variant="secondary" className="ml-auto text-xs transition-colors">
                {folder === "All Documents" ? documents.length : documents.filter((d) => d.folder === folder).length}
              </Badge>
            </Button>
          ))}
        </div>
      </div>

      {/* Document List */}
      <div className="flex-1 overflow-hidden">
        <div className="p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-sidebar-foreground">
              {selectedFolder} ({filteredDocuments.length})
            </h3>
          </div>
        </div>

        {/* Drop Zone */}
        <div
          className={`mx-4 mb-4 border-2 border-dashed rounded-lg p-6 text-center transition-all duration-300 cursor-pointer ${
            isDragOver
              ? "border-primary bg-primary/10 scale-105"
              : "border-sidebar-border hover:border-primary/50 hover:bg-primary/5"
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <Upload
            className={`h-8 w-8 mx-auto mb-2 transition-all duration-300 ${isDragOver ? "text-primary scale-110" : "text-muted-foreground"}`}
          />
          <p className="text-sm text-muted-foreground">Drop files here or click to upload</p>
        </div>

        <ScrollArea className="flex-1 px-4 pb-4">
          <div className="space-y-2">
            {filteredDocuments.map((doc) => (
              <Card
                key={doc.id}
                className="p-3 hover:bg-sidebar-accent/50 transition-all duration-200 group hover:shadow-sm hover:scale-[1.02]"
              >
                <div className="flex items-start gap-3">
                  <Checkbox
                    checked={doc.selected}
                    onCheckedChange={() => handleDocumentToggle(doc.id)}
                    className={`mt-0.5 transition-all duration-200 ${doc.selected ? "border-primary data-[state=checked]:bg-primary scale-110" : ""}`}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      {getFileIcon(doc.type)}
                      <p
                        className={`text-sm font-medium truncate transition-colors duration-200 ${doc.selected ? "text-primary" : "text-card-foreground"}`}
                      >
                        {doc.name}
                      </p>
                      {doc.selected && (
                        <Badge
                          variant="secondary"
                          className="text-xs px-1 py-0 animate-in fade-in-0 slide-in-from-right-2"
                        >
                          Context
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                      <span>{doc.size}</span>
                      <span>•</span>
                      <span>{doc.uploaded}</span>
                      <span>•</span>
                      <Badge variant="outline" className="text-xs px-1 py-0">
                        {doc.folder}
                      </Badge>
                    </div>
                    {doc.selected && doc.summary && (
                      <p className="text-xs text-muted-foreground mt-2 italic animate-in fade-in-0 slide-in-from-top-1">
                        {doc.summary}
                      </p>
                    )}
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="opacity-0 group-hover:opacity-100 transition-all duration-200 h-6 w-6 p-0 hover:bg-sidebar-accent"
                      >
                        <MoreVertical className="h-3 w-3" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="animate-in fade-in-0 slide-in-from-top-2">
                      <DropdownMenuItem className="hover:bg-sidebar-accent/50">
                        <Eye className="h-4 w-4 mr-2" />
                        Preview
                      </DropdownMenuItem>
                      <DropdownMenuItem className="hover:bg-sidebar-accent/50">
                        <Download className="h-4 w-4 mr-2" />
                        Download
                      </DropdownMenuItem>
                      <DropdownMenuItem className="text-destructive hover:bg-destructive/10">
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </Card>
            ))}
          </div>
        </ScrollArea>
      </div>
    </div>
  )
}
