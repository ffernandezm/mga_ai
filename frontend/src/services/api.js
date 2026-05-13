import axios from 'axios';

// URL del backend. En producción se configura con la variable VITE_API_URL
// (Vercel, Render, etc.). En desarrollo cae a localhost:8000.
const API_BASE_URL =
  (import.meta.env && import.meta.env.VITE_API_URL) || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export default api;
