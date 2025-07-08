// Create this file: frontend2/celestial-conversations-nexus/src/config/api.ts
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const apiEndpoints = {
  chat: `${API_BASE_URL}/chat`,
  health: `${API_BASE_URL}/health`,
};

// Example usage in your components:
// const response = await fetch(apiEndpoints.chat, { ... });
