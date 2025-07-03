# BookTalk – AI-Powered Conversational Book Companion

BookTalk enables users to have meaningful, RAG-based (retrieve-augment-generate) conversations with books. The app ensures that all answers are grounded strictly in the contents of selected books, without external influence, political bias, or AI hallucinations.

## Project Structure

The project is organized into two main parts:

1. **Frontend** - Next.js application with TypeScript
2. **Backend** - FastAPI Python server with FAISS for vector search

### Frontend Structure

- `/app` - Next.js app directory
  - `/components` - Reusable React components
  - `/login` - Authentication page
  - `/upload` - Book upload page
- `/lib` - Utility functions and API clients
- `/hooks` - Custom React hooks
- `/public` - Static assets

### Backend Structure

- `/app` - Main application package
  - `/api` - API endpoints and routers
  - `/models` - Data models and schemas
  - `/services` - Business logic services
- `requirements.txt` - Python dependencies
- `run.py` - Entry point for the FastAPI server

## Getting Started

### Setting up the Frontend

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Create a `.env.local` file based on `.env.local.example` and add your Firebase configuration.

4. Run the development server:
   ```
   npm run dev
   ```

### Setting up the Backend

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Run the server:
   ```
   python run.py
   ```

## Core Features

1. **Book Selection Panel**
   - Users can select one or multiple books
   - Search for books by title or author

2. **Conversational Chat**
   - RAG-based chat interface
   - Option to chat with the whole book or specific characters

3. **Source Chunk Display**
   - Shows source paragraphs used to generate responses
   - Ensures transparency in the AI's answers

4. **Book Upload & Embedding**
   - Users can upload their own books
   - Books can be kept private or shared with the community

5. **Firebase Integration**
   - Authentication and user management
   - Storage for books and metadata

## Environment Configuration

To run the application, you'll need to set up the following environment variables:

### Frontend (.env.local)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_firebase_auth_domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_firebase_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_firebase_storage_bucket
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_firebase_messaging_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_firebase_app_id
```

### Backend (.env)

```
GOOGLE_API_KEY=your_google_api_key
FIREBASE_CREDENTIALS_PATH=path/to/firebase_credentials.json
```

## File Processing Pipeline

When a user uploads a book, the following process takes place:

1. The file is uploaded to the server and saved temporarily
2. The book is parsed and text is extracted using the `BookParser` service
3. The text is chunked into smaller pieces for embedding
4. Embeddings are generated for each chunk using Google's embedding API
5. The book's personality and characters are extracted using Google's Gemini model
6. Chunks and embeddings are stored in the FAISS vector store
7. Book metadata is stored in Firebase

## RAG Implementation

The Retrieval-Augmented Generation (RAG) pipeline works as follows:

1. User sends a message to the chat interface
2. The message is embedded using the same embedding model
3. Similar chunks are retrieved from the FAISS vector store
4. The chunks are sent to Google's Gemini model along with the query
5. The model generates a response based only on the provided chunks
6. The response is returned to the user along with the source chunks

### Frontend Environment Variables

```
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-messaging-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend Environment Variables

Create a `.env` file in the backend directory with:

```
GOOGLE_API_KEY=your-google-api-key
FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json
```

## Contributing

Please read the contributing guidelines before submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
