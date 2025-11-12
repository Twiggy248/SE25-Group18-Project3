# 🚀 ReqEngine Backend - FastAPI Service

[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Transformers](https://img.shields.io/badge/AI-Transformers-FF6F00.svg?logo=huggingface&logoColor=white)](https://huggingface.co/transformers/)
[![ChromaDB](https://img.shields.io/badge/Vector_DB-ChromaDB-FF6B6B.svg)](https://www.trychroma.com/)
[![Pytest](https://img.shields.io/badge/Testing-Pytest-0A9EDC.svg?logo=pytest&logoColor=white)](https://pytest.org/)
[![Coverage](https://img.shields.io/badge/Coverage-pytest--cov-brightgreen.svg)](https://pytest-cov.readthedocs.io/)

High-performance backend service for intelligent requirements engineering using **Large Language Models** and **semantic analysis** to extract structured use cases from unstructured text.

---

## 🏗️ Architecture Overview

```
backend/
├── main.py                    # FastAPI application and API endpoints
├── db.py                      # SQLite database operations and schema
├── document_parser.py         # Multi-format document processing (PDF, DOCX, TXT)
├── chunking_strategy.py       # Intelligent text chunking for large documents
├── rag_utils.py              # RAG implementation and semantic search
├── use_case_enrichment.py    # LLM-based content enhancement
├── use_case_validator.py     # Quality validation and structure checking
├── export_utils.py           # Multi-format export (DOCX, Markdown, JSON, etc.)
├── requirements.txt          # Python dependencies
├── pytest.ini              # Testing configuration
└── tests/                   # Comprehensive test suite
    ├── test_main.py         # API endpoint tests
    ├── test_db.py           # Database operation tests
    ├── test_document_parser.py
    ├── test_export_utils.py
    ├── test_rag_utils.py
    └── test_integration.py  # End-to-end integration tests
```

---

## ✨ Core Features

### 🧠 AI-Powered Processing
- **Large Language Model Integration**: Uses Hugging Face Transformers with quantized models
- **Smart Use Case Estimation**: Automatically analyzes text complexity to estimate use case count
- **Dynamic Token Budgeting**: Adapts response length based on content requirements
- **Semantic Duplicate Detection**: Prevents redundant use cases using sentence embeddings

### 📄 Document Processing
- **Multi-Format Support**: PDF, DOCX, Markdown parsing
- **Intelligent Chunking**: Context-aware text splitting for large documents
- **Quality Validation**: Automatic structure and completeness checking
- **Content Enrichment**: LLM-based enhancement of sparse requirements

### 🗄️ Data Management
- **SQLite Database**: Persistent storage with optimized schema
- **Session Management**: Project context and conversation history tracking
- **Vector Storage**: ChromaDB integration for semantic search
- **Export Capabilities**: Multiple output formats (DOCX, Markdown)

---

## 📡 API Endpoints

### Core Extraction
| Endpoint | Method | Description | Request Body |
|----------|--------|-------------|--------------|
| `/parse_use_case_rag/` | POST | Extract use cases from text | `{"raw_text": str, "project_context": str, "domain": str}` |
| `/parse_use_case_document/` | POST | Extract from uploaded file | Multipart form with file and metadata |

### Session Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/session/create` | POST | Create new session |
| `/session/update` | POST | Update session context |
| `/sessions/` | GET | List all sessions |
| `/session/{id}/history` | GET | Get conversation history |
| `/session/{id}/export` | GET | Export session data |
| `/session/{id}` | DELETE | Delete session |

### Use Case Operations
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/use-case/refine` | POST | Refine specific use case components |
| `/query` | POST | Natural language queries against use cases |



---

## Installation and Setup

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Installation
1. Navigate to the backend directory:
```bash
cd proj2/backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000` with documentation at `http://localhost:8000/docs`.

---

## 📊 Test Statistics

### Comprehensive Test Suite
- **Total Tests**: 90+ comprehensive test cases
- **Coverage Target**: 80%+ code coverage maintained
- **Test Categories**: Unit, Integration, and API endpoint tests
- **Test Files**: 8 specialized test modules

### Test Breakdown
- **API Endpoint Tests**: Complete coverage of all 9 REST endpoints
- **Database Operations**: CRUD operations and schema validation
- **Document Processing**: PDF, DOCX, TXT, and Markdown parsing
- **Use Case Validation**: Quality checks and structure validation
- **Integration Tests**: End-to-end workflow testing
- **RAG Utilities**: Semantic search and embedding functionality

### Test Commands
```bash
pytest                          # Run all tests
pytest --cov=. --cov-report=html  # Run with coverage
pytest -m unit                 # Unit tests only
pytest -m integration          # Integration tests only
```




## 📄 License

This backend service is part of the ReqEngine project, licensed under the MIT License.