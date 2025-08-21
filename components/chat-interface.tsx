"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Send, Bot, User, Copy, RotateCcw, Download, Trash2, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { ContextPanel } from "./context-panel"
import { useDocumentContext } from "./context-provider"
import { apiService, type Message } from "@/lib/api"

const mockMessages: Message[] = [
  {
    id: "1",
    role: "assistant",
    content: "Hello! I can help you analyze and discuss the documents you've selected. What would you like to know?",
    timestamp: "10:30 AM",
  },
  {
    id: "2",
    role: "user",
    content: "Can you summarize the key requirements from the project documents?",
    timestamp: "10:32 AM",
  },
  {
    id: "3",
    role: "assistant",
    content: `Based on the **Technical Specification** and **API Documentation** you've selected, here are the key requirements:

## Authentication System
- OAuth 2.0 implementation with JWT tokens
- Multi-factor authentication support
- Session management with refresh tokens

## Database Architecture
- PostgreSQL as primary database
- Redis caching layer for performance
- Database migrations and versioning

## API Design
- RESTful endpoints following OpenAPI 3.0 spec
- GraphQL for complex queries
- Rate limiting and throttling

## Performance Requirements
- Sub-200ms response times for core operations
- 99.9% uptime SLA
- Horizontal scaling capability

Would you like me to elaborate on any of these areas?`,
    timestamp: "10:33 AM",
    sources: ["Technical Specification.docx", "API Documentation.md"],
  },
]

export function ChatInterface() {
  const { selectedDocuments, contextSummary } = useDocumentContext()
  const [messages, setMessages] = useState<Message[]>(mockMessages)
  const [input, setInput] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isTyping) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    }

    setMessages((prev) => [...prev, userMessage])
    const currentInput = input.trim()
    setInput("")
    setIsTyping(true)

    // Add typing indicator
    const typingMessage: Message = {
      id: "typing",
      role: "assistant",
      content: "",
      timestamp: "",
      isTyping: true,
    }
    setMessages((prev) => [...prev, typingMessage])

    try {
      // Get selected document IDs
      const selectedDocIds = selectedDocuments.map(doc => doc.id)
      
      // Use streaming chat for real-time response
      let responseContent = ""
      
      await apiService.streamChat(
        currentInput,
        selectedDocIds,
        (chunk) => {
          responseContent += chunk
          // Update the typing message with partial content
          setMessages((prev) =>
            prev.map((m) =>
              m.id === "typing"
                ? { ...m, content: responseContent, isTyping: true }
                : m
            )
          )
        }
      )

      // Remove typing indicator and add final response
      setMessages((prev) => {
        const filtered = prev.filter((m) => m.id !== "typing")
        const aiResponse: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: responseContent,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          sources: selectedDocuments.map((doc) => doc.name),
        }
        return [...filtered, aiResponse]
      })
    } catch (error) {
      console.error('Chat error:', error)
      // Remove typing indicator and add error message
      setMessages((prev) => {
        const filtered = prev.filter((m) => m.id !== "typing")
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "Sorry, I encountered an error while processing your request. Please try again.",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        }
        return [...filtered, errorMessage]
      })
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content)
  }

  const regenerateMessage = (messageId: string) => {
    // Logic to regenerate AI response
    console.log("Regenerating message:", messageId)
  }

  const clearConversation = () => {
    setMessages([mockMessages[0]]) // Keep welcome message
  }

  const exportConversation = () => {
    const conversation = messages
      .filter((m) => !m.isTyping)
      .map((m) => `${m.role.toUpperCase()}: ${m.content}`)
      .join("\n\n")

    const blob = new Blob([conversation], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "conversation.txt"
    a.click()
    URL.revokeObjectURL(url)
  }

  const formatMessage = (content: string) => {
    // Simple markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/## (.*?)$/gm, '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>')
      .replace(/- (.*?)$/gm, '<li class="ml-4">• $1</li>')
      .replace(/`(.*?)`/g, '<code class="bg-muted px-1 py-0.5 rounded text-sm">$1</code>')
  }

  return (
    <div className="flex flex-1 flex-col bg-background">
      {/* Header */}
      <div className="border-b border-border p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-serif font-semibold text-xl text-foreground">Chat with Documents</h1>
            <p className="text-sm text-muted-foreground mt-1">
              {selectedDocuments.length > 0
                ? `Using ${selectedDocuments.length} documents as context • ${messages.filter((m) => !m.isTyping).length} messages`
                : "Select documents from the sidebar to start • No context active"}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={exportConversation}>
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button variant="outline" size="sm" onClick={clearConversation}>
              <Trash2 className="h-4 w-4 mr-2" />
              Clear
            </Button>
          </div>
        </div>
      </div>

      <div className="p-4 border-b border-border">
        <ContextPanel />
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
        <div className="space-y-6 max-w-4xl mx-auto">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-4 group ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {message.role === "assistant" && (
                <Avatar className="h-8 w-8 bg-primary flex-shrink-0">
                  <AvatarFallback className="bg-primary text-primary-foreground">
                    <Bot className="h-4 w-4" />
                  </AvatarFallback>
                </Avatar>
              )}

              <div className={`max-w-[80%] ${message.role === "user" ? "order-2" : ""}`}>
                <div
                  className={`rounded-lg px-4 py-3 ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-card text-card-foreground border border-border"
                  }`}
                >
                  {message.isTyping ? (
                    <div className="flex items-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span className="text-sm">Analyzing context...</span>
                    </div>
                  ) : (
                    <div
                      className="text-sm leading-relaxed"
                      dangerouslySetInnerHTML={{ __html: formatMessage(message.content) }}
                    />
                  )}
                </div>

                {!message.isTyping && (
                  <div className="flex items-center justify-between mt-2">
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-xs ${
                          message.role === "user" ? "text-muted-foreground" : "text-muted-foreground"
                        }`}
                      >
                        {message.timestamp}
                      </span>
                      {message.sources && message.sources.length > 0 && (
                        <div className="flex items-center gap-1">
                          <Separator orientation="vertical" className="h-3" />
                          <span className="text-xs text-muted-foreground">Sources:</span>
                          {message.sources.map((source, index) => (
                            <Badge key={index} variant="outline" className="text-xs px-1 py-0">
                              {source}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0"
                        onClick={() => copyMessage(message.content)}
                      >
                        <Copy className="h-3 w-3" />
                      </Button>
                      {message.role === "assistant" && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 w-6 p-0"
                          onClick={() => regenerateMessage(message.id)}
                        >
                          <RotateCcw className="h-3 w-3" />
                        </Button>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {message.role === "user" && (
                <Avatar className="h-8 w-8 flex-shrink-0 order-3">
                  <AvatarFallback className="bg-secondary text-secondary-foreground">
                    <User className="h-4 w-4" />
                  </AvatarFallback>
                </Avatar>
              )}
            </div>
          ))}
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="border-t border-border p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-2 items-end">
            <div className="flex-1 relative">
              <Textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={
                  selectedDocuments.length > 0
                    ? "Ask a question about your documents... (Shift+Enter for new line)"
                    : "Select documents from the sidebar to start chatting..."
                }
                className="min-h-[44px] max-h-32 resize-none pr-12"
                disabled={isTyping || selectedDocuments.length === 0}
              />
              <div className="absolute bottom-2 right-2 text-xs text-muted-foreground">{input.length}/2000</div>
            </div>
            <Button
              onClick={handleSend}
              disabled={!input.trim() || isTyping || selectedDocuments.length === 0}
              className="bg-primary hover:bg-primary/90 h-11"
            >
              {isTyping ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            </Button>
          </div>

          {input.length > 1800 && (
            <p className="text-xs text-muted-foreground mt-1">{2000 - input.length} characters remaining</p>
          )}
        </div>
      </div>
    </div>
  )
}
