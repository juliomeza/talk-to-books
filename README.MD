# BookTalk – AI-Powered Conversational Book Companion

## Overview
BookTalk is a web application that enables users to have meaningful, RAG-based (retrieve-augment-generate) conversations with books. The app ensures that all answers are grounded strictly in the contents of selected books, without external influence, political bias, or generic AI hallucinations. Every answer should transparently cite the specific text fragments used to generate the response. The app is designed with modularity, modern minimalism (inspired by Jony Ive and Apple), and user trust at its core.

## Core Goals
- **Conversational Experience:** Users chat with the "soul" of a book or with individual book characters, receiving nuanced answers shaped by the book’s unique personality.
- **Full Transparency:** Each AI response displays the source paragraphs ("semantic chunks") used for the answer, so users know the information is verifiably book-based.
- **User-Centric Data:** Users can upload their own books (private) or contribute to the general library (public for all users).
- **Expandability:** Future support for avatars, flashcards, multi-level summaries, audio-only interactions, and social features.
- **Cost-Effective & Scalable:** Start with FAISS for vector search and modular Python backend (FastAPI), with Firebase for users/auth/storage. Architecture must be modular to allow seamless migration to a managed vector database (Qdrant, Pinecone, etc.) as scale grows.

## Features

1. **Book Selection Panel (Left)**
    - Searchable list of books (initially from Project Gutenberg, open license).
    - Users can select one or multiple books.
    - When multiple books are selected, the chat “personality” is a weighted fusion of all selected books’ personalities.

2. **Conversational Chat (Center)**
    - RAG pipeline: User message triggers semantic search of relevant book chunks, which are then summarized/elaborated in the answer.
    - Answers must strictly use book content and reflect the extracted personality/tone of the book or character.
    - Users can choose to “speak” with the book as a whole or as a specific character (where available).

3. **Source Chunk Display (Right)**
    - Shows all chunks (paragraphs) retrieved and used for the current answer.
    - Newest chunks for each answer are visually highlighted (animation, color, or similar).
    - Previous chunks fade or gray out over time.
    - Each chunk can be “saved” (with a + button) to the user’s personal notes for later review (for future flashcards/deeper exploration).

4. **Book Upload & Embedding**
    - Embeddings are pre-computed offline for default library, and generated on-upload for user files.
    - User-uploaded books are private by default.
    - For prototyping, use FAISS (Python library by Meta) for vector search, integrated with a FastAPI backend.
    - For authentication, user management, and file storage, use Firebase.
    - Design all data flows and APIs to be modular, enabling easy migration to a managed vector database (Qdrant, Pinecone, etc.) in the future.

5. **Personality Extraction**
    - On book import/embedding, automatically extract a personality profile for each book and for each major character (if applicable).
    - When chatting, system “acts” as either the book’s personality or a selected character.
    - When multiple books are selected, personalities are fused in a meaningful way (weighted by relevance or user interaction).

6. **UI/UX**
    - Modern, clean, light background (no dark mode by default).
    - Layout inspired by Apple minimalism (Jony Ive) and some navigation elements from Spotify (but not dark-themed).
    - Responsive design, intuitive user flows, frictionless onboarding.
    - All UI, code, and comments must be in English.

7. **Authentication**
    - Use OAuth-based authentication (Google, Facebook, etc.), but can be added in a later phase. Code should be modular to enable secure user management.

## User Stories

- As a user, I want to select a book and chat with it, knowing that all responses come directly from the book’s content.
- As a user, I want to see which paragraphs/sections were used to generate each answer, and save interesting ones to my notes.
- As a user, I want to upload my own books, keep them private, or optionally share them with the global library.
- As a user, I want to choose whether I am talking to the "book itself" or to a character in the book (if supported).
- As a user, I want to use the app in my browser without any installation.

## Technical Guidelines

- **Frontend:** React (or Next.js if preferred by the AI), using TypeScript for type safety.
- **Backend:**  
    - Use Python with FastAPI to serve a RESTful API.
    - Implement vector search with FAISS (Meta) for efficient semantic search over book embeddings (ideal for prototypes and small/mid datasets, e.g. ~10 books initially).
    - Design the backend to be modular, allowing a smooth migration to managed vector databases (Qdrant, Pinecone, etc.) as needed.
    - Use Firebase Functions and Firestore for user management, authentication, and file storage.
- **Embeddings:** Use Google’s embedding API (`text-embedding-004` or latest) for rapid prototyping, but system should be modular to allow switching to OpenAI or other providers if quality/cost tradeoff improves.
- **Storage:** Store book files, embeddings, and user notes securely. For private books, ensure only owner can access.
- **RAG Pipeline:** Implement robust, fast retrieval and generation with clear source mapping for every answer.
- **Modularity:** All features should be built as independent modules to enable future extension (avatars, audio, flashcards, etc).
- **Testing:** Automated tests for all key components and edge cases.

## Design Inspiration

- Jony Ive / Apple: Minimalism, whitespace, clarity, elegance, no visual clutter.
- Spotify: Clean navigation, discoverability, smooth transitions, but **no dark backgrounds**.
- All iconography and color palettes must enhance clarity and focus.

## Future Roadmap (Phase 2+)

- Avatars/animated book personalities
- Multi-level text/audio summaries
- Flashcard generation from saved chunks
- Audio-only conversation mode
- Social features (share quotes, notes, etc)
- Richer personalization (themes, preferences)

## Open Questions

- What is the best/most cost-effective vector DB for moderate-scale prototypes? (Evaluate FAISS, Qdrant, Pinecone, Weaviate, etc.)
- How to best extract personality profiles for books and characters in a scalable, automated way?
- (Optional) Should we support multi-language books and UI? (Out of scope for v1.)

## Architecture Diagram (Text)

User (Browser)
   │
   ▼
Frontend (React / Next.js + TypeScript)
   │
   ▼
REST API (FastAPI + Python)
   ├── FAISS (Vector Search Engine, runs on server)
   ├── Embedding Generator (calls Google Embedding API)
   └── Firebase (Authentication, User Data, File Storage)

**All code, configs, and tests must be in English. Ensure modularity and extensibility at every layer. Document decisions and code for future migration and scaling. Ask clarifying questions in comments if requirements are unclear.**
