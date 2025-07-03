# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BookTalk is an AI-powered conversational book companion that enables users to have meaningful, RAG-based conversations with books. The application ensures all answers are grounded strictly in book contents with transparent source citations.

## Architecture

The project follows a modular architecture:

```
Frontend (React/Next.js + TypeScript)
   │
   ▼
REST API (FastAPI + Python)
   ├── FAISS (Vector Search Engine)
   ├── Embedding Generator (Google Embedding API)
   └── Firebase (Authentication, User Data, File Storage)
```

## Key Technical Stack

- **Frontend**: React or Next.js with TypeScript
- **Backend**: Python with FastAPI for RESTful API
- **Vector Search**: FAISS (Meta) for semantic search over book embeddings
- **Authentication**: Firebase Functions and Firestore
- **Embeddings**: Google's embedding API (`text-embedding-004` or latest)
- **Storage**: Firebase for user management and file storage

## Core Components

### RAG Pipeline
- User message triggers semantic search of relevant book chunks
- Retrieved chunks are summarized/elaborated in responses
- All answers must strictly use book content and cite sources

### Three-Panel UI Layout
1. **Book Selection Panel (Left)**: Searchable list of books
2. **Conversational Chat (Center)**: Main chat interface
3. **Source Chunk Display (Right)**: Shows retrieved paragraphs with citations

### Personality System
- Automatic extraction of personality profiles for books and characters
- Support for chatting with book as a whole or specific characters
- Multi-book personality fusion when multiple books selected

## Development Guidelines

### Code Standards
- All code, comments, variables, functions, and documentation must be in English
- Use consistent naming conventions and follow best practices for code organization
- Ensure modularity to enable future feature integration
- Design for easy migration to managed vector databases (Qdrant, Pinecone, etc.)

### UI/UX Principles
- Modern, clean, light background (no dark mode by default)
- Inspired by Apple minimalism (Jony Ive) and Spotify navigation
- Responsive design with intuitive user flows
- Focus on transparency and user trust

### Security & Privacy
- User-uploaded books are private by default
- Secure storage for book files, embeddings, and user notes
- OAuth-based authentication support (modular implementation)

## Future Extensibility

The codebase is designed to support future features:
- Avatars/animated book personalities
- Multi-level text/audio summaries
- Flashcard generation from saved chunks
- Audio-only conversation mode
- Social features (share quotes, notes, etc.)

## Testing Requirements

- Automated tests for all key components and edge cases
- Test RAG pipeline accuracy and source attribution
- Verify privacy and security implementations