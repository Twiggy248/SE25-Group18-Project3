# 💡 ReqEngine: Intelligent Requirements Engineering Tool

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API_Framework-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React_19-61DAFB.svg?logo=react&logoColor=white)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Build_Tool-Vite-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/Styling-TailwindCSS-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Transformers](https://img.shields.io/badge/AI-Transformers-FF6F00.svg?logo=huggingface&logoColor=white)](https://huggingface.co/transformers/)
[![ChromaDB](https://img.shields.io/badge/Vector_DB-ChromaDB-FF6B6B.svg)](https://www.trychroma.com/)
[![Tests](https://github.com/Pradyumna-Chacham/CSC510-SE-Group17/actions/workflows/tests.yml/badge.svg)](https://github.com/Pradyumna-Chacham/CSC510-SE-Group17/actions)
[![Coverage](https://codecov.io/github/Pradyumna-Chacham/CSC510-SE-Group17/graph/badge.svg?token=1FJU8ZHQ0A&flag=backend)](https://codecov.io/github/Pradyumna-Chacham/CSC510-SE-Group17)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg?logo=github&logoColor=white)](https://github.com/Pradyumna-Chacham/CSC510-SE-Group17/actions)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/Pradyumna-Chacham/CSC510-SE-Group17/blob/main/proj2/LICENSE.md)
[![DOI](https://zenodo.org/badge/1044513773.svg)](https://doi.org/10.5281/zenodo.17581553)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Linting: Pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![Code Style: Prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg)](https://github.com/prettier/prettier)
[![Linting: ESLint](https://img.shields.io/badge/linting-eslint-4B32C3.svg)](https://eslint.org/)
---
## 🌟 Project Overview

**ReqEngine** is an intelligent requirements engineering tool built on **FastAPI** that uses a fine-tuned **Large Language Model (LLaMA 3.2 3B Instruct)** to automatically transform unstructured textual requirements into structured, high-quality **Use Case Specifications**. It is engineered for efficiency, accuracy, and reliability across documents of any size.

---

## 👥 Intended Users

### 🎯 Primary Users
- **Requirements Engineers**: Professionals who gather, analyze, and document software requirements
- **Business Analysts**: Specialists who bridge business needs with technical solutions
- **Product Managers**: Leaders who define product features and user stories
- **Software Architects**: Designers who need structured requirements for system design

### 🏢 Target Organizations
- **Software Development Companies**: Teams building custom applications
- **Consulting Firms**: Organizations managing multiple client projects
- **Enterprise IT Departments**: Internal teams developing business applications
- **Educational Institutions**: Academic projects and research in requirements engineering

### 💼 Use Cases
- **Legacy System Modernization**: Extract requirements from old documentation
- **Agile Sprint Planning**: Convert user stories into detailed use cases
- **Client Requirements Analysis**: Process client documents into structured specifications
- **Compliance Documentation**: Generate audit-ready requirement documentation
- **Project Handovers**: Standardize requirements across teams and vendors

---

## 🏗️ Project Structure

### Backend (FastAPI + Python)
```
backend/
├── main.py                    # FastAPI application and API endpoints
├── db.py                      # SQLite database operations
├── document_parser.py         # Multi-format document processing
├── chunking_strategy.py       # Intelligent text chunking
├── rag_utils.py              # RAG and semantic search utilities
├── use_case_enrichment.py    # LLM-based content enhancement
├── use_case_validator.py     # Quality validation logic
├── export_utils.py           # Multi-format export functionality
└── requirements.txt          # Python dependencies
```

### Frontend (React + Vite)
```
frontend/
├── src/
│   ├── components/           # Reusable UI components
│   ├── pages/               # Application pages/views
│   ├── api/                 # API client configuration
│   ├── store/               # Zustand state management
│   └── utils/               # Utility functions
├── package.json             # Node.js dependencies
├── vite.config.js          # Vite build configuration
├── tailwind.config.cjs     # TailwindCSS styling
└── eslint.config.js        # ESLint code style rules
```

---

## ✨ Key Features

### 🧠 Intelligent Requirements Processing
- **Smart Use Case Extraction**: Automatically analyzes input text to estimate the number of distinct use cases
- **Dynamic Token Budgeting**: Adapts LLM response length based on content complexity
- **Semantic Duplicate Detection**: Uses Sentence Transformers to identify and prevent duplicate requirements
- **Multi-format Document Support**: Processes PDF, DOCX, and Markdown files

### 📊 Advanced Analytics
- **Quality Validation**: Automatically validates structure and completeness of extracted use cases
- **Interactive Refinement**: Allows users to iteratively improve specific use case components
- **Natural Language Queries**: RAG-enabled querying against extracted requirements
- **Session Management**: Persistent storage of project context and conversation history

### 🚀 Export Capabilities
- **Microsoft Word (.docx)**: Professional specification documents
- **Markdown (.md)**: Documentation-ready format

---

##  Documentation

### 📋 Quick Reference
- **[Setup Guide](docs/SETUP.md)** - Quick setup instructions for development
- **[Installation Guide](docs/INSTALL.md)** - Comprehensive installation and configuration
- **[API Reference](docs/API.md)** - Complete REST API documentation with examples

### 🛠️ Development Resources
- **[Contributing Guidelines](docs/CONTRIBUTING.md)** - Development workflow and coding standards
- **[Code of Conduct](docs/CODE-OF-CONDUCT.md)** - Community guidelines and behavior standards
- **[Changelog](docs/CHANGELOG.md)** - Version history and release notes

### 🏗️ Architecture Documentation
- **[Backend README](backend/README.md)** - FastAPI backend architecture and APIs
- **[Frontend README](frontend/README.md)** - React frontend components and structure

---

## 📖 Citation

If you use ReqEngine in your research or project, please cite it as:

```bibtex
@software{reqengine2025,
  title={ReqEngine: Intelligent Requirements Engineering Tool},
  author={ReqEngine Development Team},
  year={2025},
  url={https://github.com/Pradyumna-Chacham/CSC510-SE-Group17/tree/main/proj2},
  note={AI-powered tool for transforming unstructured requirements into structured use cases}
}
```
---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.
