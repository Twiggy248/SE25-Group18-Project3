// -----------------------------------------------------------------------------
// File: client.js
// Description: API client configuration for ReqEngine frontend - handles
//              HTTP requests to the FastAPI backend with axios configuration.
// Author: Pradyumna Chacham
// Date: November 2025
// Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
// License: MIT License - see LICENSE file in the root directory.
// -----------------------------------------------------------------------------

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const api = {
  login: () => {
    window.location.href = "http://localhost:8000/auth/google"
  },

  // Session Management
  createSession: (data) => apiClient.post('/session/create', data),
  updateSession: (data) => apiClient.post('/session/update', data),
  getSessionHistory: (sessionId, limit = 10) => 
    apiClient.get(`/session/${sessionId}/history`, { params: { limit } }),
  getSessionTitle: (sessionId) => apiClient.get(`/session/${sessionId}/title`),
  getSessions: () => apiClient.get('/sessions/'),
  deleteSession: (sessionId) => apiClient.delete(`/session/${sessionId}`),
  exportSession: (sessionId) => apiClient.get(`/session/${sessionId}/export`),

  renameSession: (sessionId, newTitle) => 
    apiClient.post("/session/rename", {
      session_id: sessionId, 
      new_title: newTitle,
    }),

  // Use Case Extraction
  extractFromText: (data) => apiClient.post('/parse_use_case_rag/', data),
  
  // ✅ FIXED: Now accepts options parameter to include session_id
  extractFromDocument: (formData, options = {}) => {
    // Ensure formData includes session_id if provided in options
    if (options.session_id && !formData.has('session_id')) {
      formData.append('session_id', options.session_id);
    }
    if (options.project_context && !formData.has('project_context')) {
      formData.append('project_context', options.project_context);
    }
    if (options.domain && !formData.has('domain')) {
      formData.append('domain', options.domain);
    }
    
    return apiClient.post('/parse_use_case_document/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // Use Case Operations
  refineUseCase: (data) => apiClient.post('/use-case/refine', data),
  getSessionUseCases: (sessionId) => apiClient.get(`/session/${sessionId}/history`),

  // Query
  queryRequirements: (data) => apiClient.post('/query', data),

  // Summarization
  summarizeChatUseCases: (data) => apiClient.post('/summarize/chat_use_cases/', data),
  summarizeSession: (sessionId) => apiClient.get(`/summarize/session/${sessionId}/`),

  // Export
  exportDOCX: (sessionId) => 
    apiClient.get(`/session/${sessionId}/export/docx`, { responseType: 'blob' }),
  exportMarkdown: (sessionId) => 
    apiClient.get(`/session/${sessionId}/export/markdown`, { responseType: 'blob' }),
  exportPlantUML: (sessionId) => apiClient.get(`/session/${sessionId}/export/plantuml`),

  // Health Check
  health: () => apiClient.get('/health'),

  //Logout 
  me: () => apiClient.get('http://localhost:8000/auth/me', { withCredentials: true }),
  logout: () => apiClient.post('/auth/logout'),


};

export default apiClient;