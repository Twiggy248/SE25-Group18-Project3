# 🎨 ReqEngine Frontend - React Application

[![React](https://img.shields.io/badge/Framework-React_19-61DAFB.svg?logo=react&logoColor=white)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Build_Tool-Vite-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/Styling-TailwindCSS-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Zustand](https://img.shields.io/badge/State-Zustand-FF6B6B.svg)](https://zustand-demo.pmnd.rs/)
[![Vitest](https://img.shields.io/badge/Testing-Vitest-6E9F18.svg?logo=vitest&logoColor=white)](https://vitest.dev/)
[![ESLint](https://img.shields.io/badge/Code_Style-ESLint-4B32C3.svg?logo=eslint&logoColor=white)](https://eslint.org/)

Modern **React 19** frontend application for ReqEngine - providing an intuitive interface for intelligent requirements engineering and use case extraction.

---

## 🏗️ Project Structure

```
frontend/
├── public/                    # Static assets
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── Layout/          # Application layout components
│   │   │   ├── Header.jsx   # Main navigation header
│   │   │   ├── Sidebar.jsx  # Session management sidebar
│   │   │   └── SessionHeader.jsx # Session-specific header
│   │   ├── FileUploader.jsx # Drag-and-drop file upload
│   │   ├── LoadingSpinner.jsx # Loading state component
│   │   ├── QualityBadge.jsx # Use case quality indicator
│   │   └── UseCaseCard.jsx  # Individual use case display
│   ├── pages/               # Application pages/views
│   │   ├── Chat.jsx         # Interactive chat interface
│   │   ├── Dashboard.jsx    # Project overview dashboard
│   │   ├── Export.jsx       # Export functionality
│   │   ├── Extraction.jsx   # Text/document extraction
│   │   ├── Query.jsx        # Natural language queries
│   │   ├── SessionHistory.jsx # Session management
│   │   ├── UseCaseDetail.jsx # Detailed use case view
│   │   └── UseCaseRefine.jsx # Use case refinement
│   ├── api/                 # API client configuration
│   │   └── client.js        # Axios-based API client
│   ├── store/               # State management
│   │   └── useSessionStore.js # Zustand session store
│   ├── utils/               # Utility functions
│   │   └── formatters.js    # Date/text formatting utilities
│   ├── App.jsx              # Main application component
│   ├── main.jsx             # Application entry point
│   └── setupTests.js        # Test configuration
├── package.json             # Dependencies and scripts
├── vite.config.js          # Vite build configuration
├── tailwind.config.cjs     # TailwindCSS configuration
├── eslint.config.js        # ESLint rules and settings
└── postcss.config.cjs      # PostCSS configuration
```

---

## ✨ Key Features

### 🎯 User Interface
- **Modern Design**: Clean, responsive interface built with TailwindCSS
- **Responsive Layout**: Works seamlessly on desktop.
- **Drag & Drop**: Intuitive file upload with visual feedback

### 🔄 State Management
- **Zustand Store**: Lightweight, type-safe state management
- **Session Persistence**: Maintains context across page refreshes
- **Real-time Updates**: Automatic synchronization with backend
- **Optimistic Updates**: Immediate UI feedback for better UX

### 📱 Core Pages & Features

#### 🏠 Dashboard
- Project overview with session statistics
- Recent sessions with quick access
- Visual use case quality indicators
- Progress tracking and analytics

#### 📝 Extraction
- **Text Input**: Direct text extraction with rich editor
- **File Upload**: Support for PDF, DOCX, TXT, Markdown
- **Real-time Processing**: Live feedback during extraction

#### 💬 Chat Interface
- **Interactive Conversations**: Natural language interaction
- **Session Context**: Maintains conversation history
- **File Upload Integration**: Mid-conversation document processing
- **Use Case Refinement**: Interactive improvement of extracted content

#### 🔍 Query System
- **Natural Language Queries**: Ask questions about extracted use cases
- **Semantic Search**: Find relevant use cases by meaning
- **Export Results**: Save query results in multiple formats

#### 📊 Export Capabilities
- **Multiple Formats**: DOCX, Markdown, PDF

---

## 🚀 Installation & Setup

### Prerequisites
- **Node.js 18+**
- **npm** 
- **Backend service** running on http://localhost:8000

### Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Open in browser:**
   ```
   http://localhost:5173
   ```

---

## 🧪 Testing

### Test Structure
```
src/
├── components/__tests__/    # Component unit tests
├── pages/__tests__/        # Page integration tests
├── api/__tests__/          # API client tests
├── store/__tests__/        # State management tests
└── utils/__tests__/        # Utility function tests
```

### Running Tests

```bash
# Watch mode for development
npm test

# Single run with coverage
npm run test:coverage

# Interactive UI
npm run test:ui

# Specific test file
npm test -- FileUploader.test.jsx
```

### Test Coverage
- **Target**: 80%+ code coverage maintained
- **Test Types**: Component unit tests, page integration tests, API client tests
- **Total Tests**: 100+ test cases across all modules

---

## 🎨 Styling & Design

### TailwindCSS Configuration
```javascript
// tailwind.config.cjs
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        primary: '#4F46E5',    // Indigo
        success: '#10B981',    // Emerald
        warning: '#F59E0B',    // Amber
        error: '#EF4444',      // Red
      }
    },
  }
}
```

### Design System
- **Color Palette**: Consistent color scheme across components
- **Typography**: Responsive text sizing and spacing
- **Components**: Reusable styled components
- **Responsive**: Mobile-first responsive design


---

## 🌐 API Integration

### API Client (`src/api/client.js`)
```javascript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

export const api = {
  // Session management
  createSession: (data) => apiClient.post('/session/create', data),
  getSessions: () => apiClient.get('/sessions/'),
  
  // Use case extraction
  extractFromText: (data) => apiClient.post('/parse_use_case_rag/', data),
  extractFromFile: (formData) => apiClient.post('/parse_use_case_document/', formData),
  
  // Queries and refinement
  queryUseCases: (data) => apiClient.post('/query', data),
  refineUseCase: (data) => apiClient.post('/use-case/refine', data),
};
```

### Error Handling
```javascript
// API error interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data);
    return Promise.reject(error);
  }
);
```

---

## 🔄 State Management

### Zustand Store Structure
```javascript
// src/store/useSessionStore.js
const useSessionStore = create((set, get) => ({
  // Session state
  currentSessionId: null,
  sessionTitle: '',
  sessions: [],
  
  // Project context
  projectContext: '',
  domain: '',
  useCases: [],
  
  // Actions
  setCurrentSession: (sessionId, title) => set({ currentSessionId: sessionId, sessionTitle: title }),
  setSessions: (sessions) => set({ sessions }),
  clearSession: () => set({ /* reset state */ }),
}));
```

### State Actions
- **Session Management**: Create, switch, and clear sessions
- **Use Case Management**: Add, update, and organize use cases
- **UI State**: Loading states, error handling, notifications

---

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Errors**
   ```javascript
   // Check backend server status
   curl http://localhost:8000/health
   ```

2. **Build Failures**
   ```bash
   # Clear node_modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Styling Issues**
   ```bash
   # Rebuild Tailwind CSS
   npm run dev
   ```

---

## 🤝 Contributing

### Development Workflow
1. **Create feature branch**: `git checkout -b feature/amazing-feature`
2. **Install dependencies**: `npm install`
3. **Start development**: `npm run dev`
4. **Write tests**: Add tests for new features
5. **Run quality checks**: `npm run lint && npm test`
6. **Submit PR**: With description and test results

---

## 📄 License

This frontend application is part of the ReqEngine project, licensed under the MIT License.