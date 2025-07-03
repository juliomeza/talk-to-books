import axios from 'axios';

// Create an axios instance with the base URL from environment variables
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include the auth token in requests
api.interceptors.request.use(async (config) => {
  // This would normally get the token from a secure source
  // For now, we'll get it from localStorage in the browser
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.token = token;
    }
  }
  return config;
});

// Book API endpoints
export const booksApi = {
  // Get all books
  getBooks: async () => {
    try {
      const response = await api.get('/books');
      return response.data;
    } catch (error) {
      console.error('Error fetching books:', error);
      throw error;
    }
  },

  // Get a specific book
  getBook: async (bookId: string) => {
    try {
      const response = await api.get(`/books/${bookId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching book ${bookId}:`, error);
      throw error;
    }
  },

  // Upload a book
  uploadBook: async (formData: FormData) => {
    try {
      const response = await api.post('/books/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error uploading book:', error);
      throw error;
    }
  },
};

// Chat API endpoints
export const chatApi = {
  // Send a chat message
  sendMessage: async (
    bookIds: string[],
    messages: { role: string; content: string }[],
    characterId?: string
  ) => {
    try {
      const response = await api.post('/chat', {
        book_ids: bookIds,
        messages,
        character_id: characterId,
      });
      return response.data;
    } catch (error) {
      console.error('Error sending chat message:', error);
      throw error;
    }
  },
};

export default api;
