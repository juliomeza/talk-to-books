"use client";

import { useState } from "react";
import BookUploadForm from "../components/BookUploadForm";
import Link from "next/link";

export default function Upload() {
  return (
    <main className="flex min-h-screen flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">
            <Link href="/" className="hover:text-blue-600">
              BookTalk
            </Link>
          </h1>
          <nav>
            <ul className="flex space-x-6">
              <li>
                <Link href="/" className="text-blue-600 hover:text-blue-800">
                  Back to Chat
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
      <div className="container mx-auto px-4 py-8 flex-grow">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold mb-6 text-center">Upload a New Book</h2>
          <p className="text-gray-600 mb-8 text-center">
            Upload your own books to chat with them. Books can be kept private or shared with the global library.
          </p>
          
          <BookUploadForm />
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
