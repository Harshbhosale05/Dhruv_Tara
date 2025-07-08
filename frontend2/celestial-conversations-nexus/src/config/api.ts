// API Configuration - Production Ready
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://dhruv-tara-2.onrender.com';

export const apiEndpoints = {
  chat: `${API_BASE_URL}/chat`,
  health: `${API_BASE_URL}/health`,
};

// Fetch wrapper with error handling
export const apiClient = {
  async chat(message: string) {
    try {
      const response = await fetch(apiEndpoints.chat, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          query: message,
          user_id: 'frontend_user' 
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Chat API error:', error);
      throw error;
    }
  },
  
  async healthCheck() {
    try {
      const response = await fetch(apiEndpoints.health);
      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      return { status: 'error', message: error.message };
    }
  }
};

// Log current configuration (only in development)
if (import.meta.env.DEV) {
  console.log('API Configuration:', {
    BASE_URL: API_BASE_URL,
    ENDPOINTS: apiEndpoints
  });
}
