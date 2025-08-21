import { Header } from "@/components/header"
import { DocumentSidebar } from "@/components/document-sidebar"
import { ChatInterface } from "@/components/chat-interface"
import { DocumentContextProvider } from "@/components/context-provider"

export default function HomePage() {
  return (
    <DocumentContextProvider>
      <div className="flex h-screen flex-col">
        <Header />
        <div className="flex flex-1 overflow-hidden">
          <DocumentSidebar />
          <ChatInterface />
        </div>
      </div>
    </DocumentContextProvider>
  )
}
