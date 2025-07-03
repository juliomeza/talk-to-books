"use client";

import React, { useState, useEffect } from "react";
import { booksApi } from "@/lib/api";

interface Book {
  id: string;
  title: string;
  author: string;
  description: string;
  cover_image?: string;
  is_public: boolean;
  characters?: { id: string; name: string }[];
}

interface BookSelectorProps {
  onSelectBooks: (selectedBooks: Book[]) => void;
}

export default function BookSelector({ onSelectBooks }: BookSelectorProps) {
  const [books, setBooks] = useState<Book[]>([]);
  const [selectedBookIds, setSelectedBookIds] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch books on component mount
  useEffect(() => {
    const fetchBooks = async () => {
      try {
        setLoading(true);
        const data = await booksApi.getBooks();
        setBooks(data);
        setError(null);
      } catch (err) {
        setError("Failed to load books. Please try again later.");
        console.error("Error loading books:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchBooks();
  }, []);

  // Filter books based on search query
  const filteredBooks = books.filter((book) => {
    const query = searchQuery.toLowerCase();
    return (
      book.title.toLowerCase().includes(query) ||
      book.author.toLowerCase().includes(query)
    );
  });

  // Handle book selection/deselection
  const toggleBookSelection = (bookId: string) => {
    setSelectedBookIds((prevSelectedIds) => {
      const newSelectedIds = prevSelectedIds.includes(bookId)
        ? prevSelectedIds.filter((id) => id !== bookId)
        : [...prevSelectedIds, bookId];
      
      // Notify parent component about selection change
      const selectedBooks = books.filter((book) => newSelectedIds.includes(book.id));
      onSelectBooks(selectedBooks);
      
      return newSelectedIds;
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 h-full flex flex-col">
      <h2 className="text-xl font-semibold mb-4">Book Selection</h2>
      
      {/* Search box */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search books..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>
      
      {/* Book list */}
      <div className="flex-grow overflow-y-auto">
        {loading ? (
          <div className="flex justify-center items-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        ) : error ? (
          <div className="text-red-500 text-center">{error}</div>
        ) : filteredBooks.length === 0 ? (
          <div className="text-gray-500 text-center">No books found</div>
        ) : (
          <ul className="space-y-2">
            {filteredBooks.map((book) => (
              <li key={book.id} className="flex items-start">
                <input
                  type="checkbox"
                  id={`book-${book.id}`}
                  checked={selectedBookIds.includes(book.id)}
                  onChange={() => toggleBookSelection(book.id)}
                  className="mt-1 mr-2"
                />
                <label htmlFor={`book-${book.id}`} className="cursor-pointer flex-grow">
                  <div className="font-medium">{book.title}</div>
                  <div className="text-sm text-gray-600">by {book.author}</div>
                </label>
              </li>
            ))}
          </ul>
        )}
      </div>
      
      {/* Selected count */}
      <div className="mt-4 text-sm text-gray-600">
        {selectedBookIds.length} {selectedBookIds.length === 1 ? "book" : "books"} selected
      </div>
    </div>
  );
}
