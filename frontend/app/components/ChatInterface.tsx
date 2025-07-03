"use client";

import React, { useState, useRef, useEffect } from "react";
import { chatApi } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface SourceChunk {
  text: string;
  book_id: string;
  page?: number;
  chunk_id: string;
}

interface Book {
  id: string;
  title: string;
  author: string;
  description: string;
  cover_image?: string;
  is_public: boolean;
  characters?: { id: string; name: string }[];
}

interface ChatInterfaceProps {
  selectedBooks: Book[];
  selectedCharacter?: { id: string; name: string } | null;
}

export default function ChatInterface({ selectedBooks, selectedCharacter }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sources, setSources] = useState<SourceChunk[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom of chat when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (newMessage.trim() === "" || selectedBooks.length === 0) {
      return;
    }
    
    // Add user message to chat
    const userMessage: Message = { role: "user", content: newMessage };
    setMessages((prev) => [...prev, userMessage]);
    setNewMessage("");
    setIsLoading(true);
    
    try {
      // Get book IDs
      const bookIds = selectedBooks.map((book) => book.id);
      
      // Send message to API
      const response = await chatApi.sendMessage(
        bookIds,
        [...messages, userMessage],
        selectedCharacter?.id
      );
      
      // Add assistant response to chat
      const assistantMessage: Message = {
        role: "assistant",
        content: response.message,
      };
      
      setMessages((prev) => [...prev, assistantMessage]);
      
      // Update sources
      setSources(response.sources);
    } catch (error) {
      console.error("Error sending message:", error);
      
      // Add error message
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-full">
      {/* Chat area */}
      <div className="flex-grow bg-white rounded-lg shadow-md p-4 mr-4 flex flex-col">
        <div className="mb-4">
          <h2 className="text-xl font-semibold">
            {selectedBooks.length === 0
              ? "Select books to start chatting"
              : selectedCharacter
              ? `Chatting with ${selectedCharacter.name}`
              : `Chatting with ${selectedBooks.length === 1 ? selectedBooks[0].title : "multiple books"}`}
          </h2>
        </div>
        
        {/* Messages container */}
        <div className="flex-grow overflow-y-auto mb-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-gray-500 text-center h-full flex items-center justify-center">
              <p>Start the conversation by sending a message</p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg ${
                  msg.role === "user" ? "bg-blue-100 ml-auto" : "bg-gray-100"
                } max-w-[80%] ${msg.role === "user" ? "ml-auto" : "mr-auto"}`}
              >
                <p>{msg.content}</p>
              </div>
            ))
          )}
          {isLoading && (
            <div className="p-3 rounded-lg bg-gray-100 max-w-[80%]">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        {/* Message input */}
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <input
            type="text"
            placeholder={selectedBooks.length === 0 ? "Select books to start chatting" : "Type your message..."}
            className="flex-grow px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            disabled={selectedBooks.length === 0 || isLoading}
          />
          <button
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-300 disabled:cursor-not-allowed"
            disabled={newMessage.trim() === "" || selectedBooks.length === 0 || isLoading}
          >
            Send
          </button>
        </form>
      </div>
      
      {/* Source chunks area */}
      <div className="w-1/3 bg-white rounded-lg shadow-md p-4 flex flex-col">
        <h2 className="text-xl font-semibold mb-4">Source Chunks</h2>
        
        <div className="flex-grow overflow-y-auto">
          {sources.length === 0 ? (
            <div className="text-gray-500 text-center h-full flex items-center justify-center">
              <p>Sources will appear here</p>
            </div>
          ) : (
            <div className="space-y-4">
              {sources.map((source, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <p className="text-sm mb-2">{source.text}</p>
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>
                      Book: {selectedBooks.find(b => b.id === source.book_id)?.title || source.book_id}
                    </span>
                    {source.page && <span>Page: {source.page}</span>}
                    <button className="text-blue-500 hover:underline">
                      Save +
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
