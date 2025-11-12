# 📝 Changelog - ReqEngine

All notable changes to the ReqEngine project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).


## [1.0.0] - 2025-11-06

### 🎉 Initial Release

#### Added
- **Core AI Features**
  - LLM-based use case extraction from unstructured text
  - Smart use case estimation and dynamic token budgeting
  - Semantic duplicate detection using sentence transformers
  - Interactive use case refinement capabilities

- **Document Processing**
  - Multi-format document support (PDF, DOCX, TXT, Markdown)
  - Intelligent text chunking for large documents
  - Quality validation and automatic content enrichment
  - Drag-and-drop file upload interface

- **Backend Infrastructure**
  - FastAPI-based REST API with 12 core endpoints
  - SQLite database with optimized schema for sessions and use cases
  - ChromaDB integration for vector storage and semantic search
  - Comprehensive error handling and logging

- **Frontend Application**
  - Modern React 19 application with Vite build system
  - TailwindCSS-based responsive UI design
  - Zustand state management for session handling
  - Real-time chat interface for interactive requirements engineering

- **Export Capabilities**
  - Microsoft Word (.docx) professional documents
  - Markdown (.md) for documentation integration
  - JSON structured data export
  - PlantUML code generation for use case diagrams
  - HTML web-ready presentations

- **Session Management**
  - Persistent session storage with conversation history
  - Project context and domain specification
  - Session title auto-generation using LLM
  - Export and deletion capabilities

- **Testing Infrastructure**
  - Backend: Pytest with 80%+ coverage target
  - Frontend: Vitest with React Testing Library
  - Integration tests for end-to-end workflows
  - Comprehensive test suites for all major components

### 🛠️ Technical Implementation
- **AI Models**: Integration with Hugging Face Transformers
- **Performance**: 4-bit quantization for memory optimization
- **Database**: SQLite with proper indexing and relationships
- **Security**: Input validation and file upload restrictions
- **Documentation**: Comprehensive README and API documentation

---

## Development Milestones

### Phase 1: Core Backend (Completed)
- ✅ FastAPI application structure
- ✅ Database schema and operations
- ✅ LLM integration and use case extraction
- ✅ Document parsing capabilities

### Phase 2: Advanced AI Features (Completed)
- ✅ Smart use case estimation
- ✅ Quality validation system
- ✅ Interactive refinement capabilities

### Phase 3: Frontend Development (Completed)
- ✅ React application with modern UI
- ✅ State management and API integration
- ✅ File upload and chat interfaces
- ✅ Export functionality

### Phase 4: Testing & Documentation (Completed)
- ✅ Comprehensive test suites
- ✅ API documentation
- ✅ User guides and setup instructions
- ✅ Code quality and linting

---

## 🔧 Technical Debt & Known Issues

### Current Limitations
- **Performance**: Large documents (>50MB) may require processing time optimization
- **Scalability**: Single-user session model (not multi-tenant)
- **Authentication**: No user authentication system implemented
- **Rate Limiting**: API endpoints not rate-limited

### Planned Improvements
- Database migration to PostgreSQL for production scalability
- Implement Redis caching for improved performance
- Add user authentication and authorization
- Containerization with Docker for easier deployment

---

## 📊 Statistics

### Codebase Metrics (v1.0.0)
- **Backend**: ~2,100 lines of Python code
- **Frontend**: ~3,500 lines of JavaScript/JSX code
- **Tests**: 45+ test files with comprehensive coverage
- **Documentation**: 8 detailed documentation files

### Features Implemented
- ✅ 12 REST API endpoints
- ✅ 8 React page components
- ✅ 15+ reusable UI components
- ✅ 5 export formats supported
- ✅ Multi-format document processing

---

## 🤝 Contributors

### Core Development Team
- **Pradyumna Chacham** 
- **Sai Mahathi Suryadevara** 
- **Sadana Ragoor** 
- **Sai Sumedh Kaveti** 

### Academic Context
- **Course**: CSC510 - Software Engineering
- **Institution**: North Carolina State University
- **Semester**: Fall 2025

---

## 📚 Dependencies

### Major Version Updates
- **React**: 19.1.1 (latest)
- **FastAPI**: 0.104.1 (stable)
- **PyTorch**: Latest CUDA 12.1 compatible
- **Transformers**: 4.38.0+ (for latest model support)

### Security Updates
- All dependencies regularly updated for security patches
- Vulnerability scanning integrated into CI/CD pipeline
- Regular dependency audits performed

---

## 🔮 Future Roadmap

### Version 2.0.0 (Future)
-Smart Use Case Summarization
 Automatically create short summaries for use cases. Helps stakeholders grasp the core idea without reading long descriptions.

-Customizable Use Case Card Themes
 Switch between Light, Dark, or Colorful modes. Apply custom layouts and colors to make the tool personal and engaging.

-User-Defined Session Renaming
 Allow users to rename sessions directly from the sidebar. Makes session lists meaningful and easier to organize.

-User Authentication & Accounts
 Secure login and account management for personalized work. Enables team collaboration while keeping projects private.

---

For detailed installation and setup instructions, see [INSTALL.md](INSTALL.md).
For contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).