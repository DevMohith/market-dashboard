import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_APP_API_BASE_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// REMOVED: Request interceptor for authentication tokens
// REMOVED: Response interceptor for error handling, e.g., redirect on 401

export default api;