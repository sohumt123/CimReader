// API Configuration for both development and production
export const API_BASE_URL = import.meta.env.PROD 
  ? import.meta.env.VITE_API_URL || 'https://cimreader.onrender.com'  // Your Render backend URL
  : 'http://localhost:8000';  // In development, use local FastAPI server

export const createApiUrl = (endpoint: string): string => {
  // Remove leading slash from endpoint if present
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  return `${API_BASE_URL}/${cleanEndpoint}`;
};

// Helper function for authenticated requests
export const createAuthHeaders = (token: string) => ({
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
});

// Helper function for multipart form data requests
export const createAuthHeadersMultipart = (token: string) => ({
  'Authorization': `Bearer ${token}`,
}); 