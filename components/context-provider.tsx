"use client"

import type React from "react"

import { createContext, useContext, useState, useCallback, useEffect } from "react"
import { apiService, type Document } from "@/lib/api"

interface ContextState {
  documents: Document[]
  selectedDocuments: Document[]
  contextSummary: string
  isContextLoading: boolean
  isLoading: boolean
  error: string | null
}

interface ContextActions {
  toggleDocument: (id: string) => void
  updateDocuments: (documents: Document[]) => void
  clearContext: () => void
  refreshContext: () => void
  loadDocuments: () => Promise<void>
  uploadDocuments: (files: File[]) => Promise<void>
  deleteDocument: (id: string) => Promise<void>
}

const DocumentContext = createContext<(ContextState & ContextActions) | null>(null)

const mockDocuments: Document[] = [
  {
    id: "1",
    name: "Project Requirements.pdf",
    size: "2.4 MB",
    uploaded: "2 hours ago",
    selected: false,
    type: "pdf",
    folder: "Projects",
    summary: "Outlines core project objectives, user stories, and technical requirements for the new platform.",
  },
  {
    id: "2",
    name: "Technical Specification.docx",
    size: "1.8 MB",
    uploaded: "1 day ago",
    selected: true,
    type: "docx",
    folder: "Projects",
    summary: "Detailed technical architecture, API specifications, and implementation guidelines.",
  },
  {
    id: "3",
    name: "User Research Report.pdf",
    size: "5.2 MB",
    uploaded: "3 days ago",
    selected: false,
    type: "pdf",
    folder: "Research",
    summary: "Comprehensive user research findings, personas, and behavioral insights.",
  },
  {
    id: "4",
    name: "API Documentation.md",
    size: "0.8 MB",
    uploaded: "1 week ago",
    selected: true,
    type: "md",
    folder: "Documentation",
    summary: "Complete API reference with endpoints, authentication, and usage examples.",
  },
  {
    id: "5",
    name: "Meeting Notes.txt",
    size: "0.2 MB",
    uploaded: "2 days ago",
    selected: false,
    type: "txt",
    folder: "Notes",
    summary: "Weekly team meeting notes covering project updates and decisions.",
  },
]

export function DocumentContextProvider({ children }: { children: React.ReactNode }) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [isContextLoading, setIsContextLoading] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const selectedDocuments = documents.filter((doc) => doc.selected)

  const contextSummary =
    selectedDocuments.length > 0
      ? `Context includes ${selectedDocuments.length} documents: ${selectedDocuments.map((d) => d.name).join(", ")}`
      : "No documents selected for context"

  const toggleDocument = useCallback((id: string) => {
    setDocuments((prev) => prev.map((doc) => (doc.id === id ? { ...doc, selected: !doc.selected } : doc)))
  }, [])

  const updateDocuments = useCallback((newDocuments: Document[]) => {
    setDocuments(newDocuments)
  }, [])

  const clearContext = useCallback(() => {
    setDocuments((prev) => prev.map((doc) => ({ ...doc, selected: false })))
  }, [])

  const loadDocuments = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const docs = await apiService.getDocuments()
      setDocuments(docs.map(doc => ({ ...doc, selected: false })))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents')
      console.error('Failed to load documents:', err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const uploadDocuments = useCallback(async (files: File[]) => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await apiService.uploadDocuments(files)
      if (response.success && response.documents) {
        setDocuments(prev => [...prev, ...response.documents!.map(doc => ({ ...doc, selected: false }))])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload documents')
      console.error('Failed to upload documents:', err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const deleteDocument = useCallback(async (id: string) => {
    try {
      await apiService.deleteDocument(id)
      setDocuments(prev => prev.filter(doc => doc.id !== id))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete document')
      console.error('Failed to delete document:', err)
    }
  }, [])

  const refreshContext = useCallback(async () => {
    setIsContextLoading(true)
    // Simulate context refresh
    await new Promise((resolve) => setTimeout(resolve, 1000))
    setIsContextLoading(false)
  }, [])

  // Load documents on mount
  useEffect(() => {
    loadDocuments()
  }, [loadDocuments])

  const value = {
    documents,
    selectedDocuments,
    contextSummary,
    isContextLoading,
    isLoading,
    error,
    toggleDocument,
    updateDocuments,
    clearContext,
    refreshContext,
    loadDocuments,
    uploadDocuments,
    deleteDocument,
  }

  return <DocumentContext.Provider value={value}>{children}</DocumentContext.Provider>
}

export function useDocumentContext() {
  const context = useContext(DocumentContext)
  if (!context) {
    throw new Error("useDocumentContext must be used within a DocumentContextProvider")
  }
  return context
}
