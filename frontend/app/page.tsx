"use client";

import { useState } from "react";
import BookSelector from "./components/BookSelector";
import ChatInterface from "./components/ChatInterface";
import Link from "next/link";

interface Book {
  id: string;
  title: string;
  author: string;
  description: string;
  cover_image?: string;
  is_public: boolean;
  characters?: { id: string; name: string }[];
}

export default function Home() {
  const [selectedBooks, setSelectedBooks] = useState<Book[]>([]);
  const [selectedCharacter, setSelectedCharacter] = useState<{ id: string; name: string } | null>(null);
  const [showCharacterSelector, setShowCharacterSelector] = useState(false);

  // Handle book selection
  const handleSelectBooks = (books: Book[]) => {
    setSelectedBooks(books);
    setSelectedCharacter(null);
    setShowCharacterSelector(books.length > 0);
  };

  // Get all characters from selected books
  const availableCharacters = selectedBooks
    .flatMap((book) => book.characters || [])
    .filter((character): character is { id: string; name: string } => !!character);

  return (
    <main className="flex min-h-screen flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">BookTalk</h1>
          <nav>
            <ul className="flex space-x-6">
              <li>
                <Link href="/upload" className="text-blue-600 hover:text-blue-800">
                  Upload Book
                </Link>
              </li>
              <li>
                <Link href="/login" className="text-blue-600 hover:text-blue-800">
                  Sign In
                </Link>
              </li>
            </ul>
          </nav>
        </div>
      </header>

      {/* Main content */}
      <div className="container mx-auto px-4 py-8 flex-grow flex">
        {/* Left sidebar - Book selection */}
        <div className="w-1/4 pr-4">
          <BookSelector onSelectBooks={handleSelectBooks} />
        </div>

        {/* Main chat area */}
        <div className="w-3/4 flex flex-col">
          {/* Character selector (if books are selected) */}
          {showCharacterSelector && availableCharacters.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-4 mb-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium">Chat with:</h3>
                <div className="flex space-x-2">
                  <button
                    className={`px-3 py-1 rounded-md ${
                      selectedCharacter === null
                        ? "bg-blue-500 text-white"
                        : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                    }`}
                    onClick={() => setSelectedCharacter(null)}
                  >
                    Whole Book
                  </button>
                  <div className="relative">
                    <button
                      className={`px-3 py-1 rounded-md ${
                        selectedCharacter !== null
                          ? "bg-blue-500 text-white"
                          : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                      }`}
                      onClick={() => setShowCharacterSelector(!showCharacterSelector)}
                    >
                      {selectedCharacter ? selectedCharacter.name : "Character"}
                    </button>
                    {showCharacterSelector && (
                      <div className="absolute top-full left-0 mt-1 w-48 bg-white rounded-md shadow-lg z-10">
                        <ul className="py-1">
                          {availableCharacters.map((character) => (
                            <li key={character.id}>
                              <button
                                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                onClick={() => {
                                  setSelectedCharacter(character);
                                  setShowCharacterSelector(false);
                                }}
                              >
                                {character.name}
                              </button>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Chat interface */}
          <div className="flex-grow">
            <ChatInterface
              selectedBooks={selectedBooks}
              selectedCharacter={selectedCharacter}
            />
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white shadow-inner mt-8">
        <div className="container mx-auto px-4 py-4 text-center text-gray-500 text-sm">
          BookTalk © {new Date().getFullYear()} - All answers are based solely on the content of selected books
        </div>
      </footer>
    </main>
  );
}
