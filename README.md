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

## 📋 Use Case Examples

### 🏦 **Example 1: E-commerce Platform**

**Input Text:**
> "The system should allow customers to browse products, add items to their shopping cart, and checkout securely. Customers must be able to create accounts, login, and view their order history. The system should send email confirmations after purchases."

**ReqEngine Output:**
- **Use Case 1**: Customer Account Registration
- **Use Case 2**: Customer Login Authentication  
- **Use Case 3**: Product Catalog Browsing
- **Use Case 4**: Shopping Cart Management
- **Use Case 5**: Secure Payment Processing
- **Use Case 6**: Order History Viewing
- **Use Case 7**: Email Notification System

---

### 🏥 **Example 2: Healthcare Management System**

**Input Document:** *Patient Management Requirements (PDF)*
> "Healthcare providers need to manage patient records, schedule appointments, and track medical history. The system must ensure HIPAA compliance and allow different access levels for doctors, nurses, and administrative staff."

**ReqEngine Output:**
```json
{
  "id": 1,
  "title": "Healthcare Provider Manages Patient Records",
  "preconditions": [
    "Provider has valid credentials",
    "Patient exists in system",
    "HIPAA compliance enabled"
  ],
  "main_flow": [
    "Provider logs into system",
    "Provider searches for patient",
    "System displays patient record",
    "Provider reviews/updates medical information"
  ],
  "stakeholders": ["Healthcare Provider", "Patient", "System Administrator"]
}
```

---

### 💰 **Example 3: Banking Application**

**Input:** *Legacy System Documentation*
> "Account holders should be able to transfer money between accounts, check balances, and receive transaction alerts. The system must support multiple currencies and comply with financial regulations."

**Generated Use Cases:**
1. **Account Balance Inquiry** - Real-time balance checking
2. **Inter-Account Money Transfer** - Secure fund transfers  
3. **Transaction Alert Management** - SMS/Email notifications
4. **Multi-Currency Support** - Currency conversion handling
5. **Regulatory Compliance Reporting** - Audit trail generation

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



## 🔍 Structured Output Example

When processing a requirement like: "*The user must be able to securely login to their account and search for products using keywords. If an item is out of stock, the system must notify the user.*", ReqEngine separates the compound actions into distinct, structured use cases.

The JSON output will contain an array of objects structured as follows:

```json
[
  {
    "id": 1,
    "title": "User Logs In To System",
    "preconditions": [
      "User has valid credentials"
    ],
    "main_flow": [
      "User opens login screen",
      "User enters credentials",
      "System validates credentials",
      "System authenticates user"
    ],
    "sub_flows": [
      "User can reset password"
    ],
    "alternate_flows": [
      "If invalid credentials: System shows error message"
    ],
    "outcomes": [
      "User is logged in successfully"
    ],
    "stakeholders": [
      "User",
      "Authentication System"
    ]
  },
  {
    "id": 2,
    "title": "User Searches For Products",
    "preconditions": [
      "User is logged in",
      "Product catalog is available"
    ],
    "main_flow": [
      "User navigates to search bar",
      "User enters keywords",
      "System returns matching products"
    ],
    "sub_flows": [
      "User can filter and sort results"
    ],
    "alternate_flows": [
      "If no match: System displays 'No results found'",
      "If item out of stock: System notifies user"
    ],
    "outcomes": [
      "Relevant product list is displayed"
    ],
    "stakeholders": [
      "User",
      "Inventory System"
    ]
  }
]
```

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes and add tests
4. Run quality checks:
   ```bash
   # Backend
   cd backend && pytest --cov=.
   
   # Frontend  
   cd frontend && npm run lint && npm test
   ```
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## � Troubleshooting

### 🚨 Common Issues and Solutions

#### **Backend Issues**

**1. Model Loading Errors**
```bash
# Problem: HuggingFace authentication failed
# Error: "Repository not found" or "Access denied"

# Solution: Set up HuggingFace token
export HF_TOKEN="your_huggingface_token_here"
# Windows: set HF_TOKEN=your_huggingface_token_here

# Verify token: 
huggingface-cli login
```

**2. CUDA/GPU Memory Issues**
```bash
# Problem: "RuntimeError: CUDA out of memory"
# Solution: Force CPU usage
export CUDA_VISIBLE_DEVICES=""

# Or reduce batch size in main.py
# max_length=1024  # Instead of 4096
```

**3. Database Lock Errors**
```bash
# Problem: "database is locked"
# Solution: Close all connections and restart
pkill -f "python main.py"
rm -f requirements.db test_requirements*.db
python main.py
```

**4. Vector Store Issues**
```bash
# Problem: ChromaDB dimension errors
# Solution: Reset vector store
rm -rf vector_store/
# Restart the application to rebuild embeddings
```

#### **Frontend Issues**

**5. Module Not Found Errors**
```bash
# Problem: "Module not found" or dependency issues
# Solution: Clean install
rm -rf node_modules package-lock.json
npm install

# Verify Node.js version (requires 18+)
node --version
```

**6. Build Failures**
```bash
# Problem: Vite build fails
# Solution: Clear cache and rebuild
npm run build --clear-cache

# Check for ESLint errors
npm run lint
```

**7. API Connection Issues**
```bash
# Problem: Frontend can't connect to backend
# Solution: Verify backend is running
curl http://localhost:8000/health

# Check CORS settings in main.py
# Ensure frontend URL is allowed
```

#### **Installation Issues**

**8. Python Version Conflicts**
```bash
# Problem: Python version incompatibility
# Solution: Use Python 3.9+
python --version  # Should show 3.9+

# Create fresh virtual environment
python -m venv fresh_venv
source fresh_venv/bin/activate  # Linux/Mac
fresh_venv\Scripts\activate      # Windows
```

**9. Dependency Conflicts**
```bash
# Problem: Package version conflicts
# Solution: Install specific versions
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**10. Port Already in Use**
```bash
# Problem: "Address already in use"
# Solution: Find and kill processes
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

### 🆘 Getting Help

**Before Reporting Issues:**
1. Check this troubleshooting guide
2. Search [existing GitHub issues](https://github.com/Pradyumna-Chacham/CSC510-SE-Group17/issues)
3. Verify you're using supported versions (Python 3.9+, Node.js 18+)

**When Reporting Issues:**
- Include error messages (full stack traces)
- Specify your operating system and versions
- Provide steps to reproduce the problem
- Attach relevant log files if available

**Support Channels:**
- **GitHub Issues**: Primary support channel
- **Documentation**: See [docs/](docs/) folder for detailed guides
- **Contributing**: See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development help

---

## 🆘 Support

### 📧 Contact Us

For questions, support, or collaboration inquiries, reach out to us:

**Email**: [reqenginequery@gmail.com](mailto:reqenginequery@gmail.com)

### 🔗 Additional Support Resources

- **🐛 Bug Reports**: [GitHub Issues](https://github.com/Pradyumna-Chacham/CSC510-SE-Group17/issues)
- **💡 Feature Requests**: [GitHub Issues](https://github.com/Pradyumna-Chacham/CSC510-SE-Group17/issues)
- **� Documentation**: [Project Documentation](docs/)
- **🤝 Contributing**: [Contributing Guidelines](docs/CONTRIBUTING.md)
- **❓ Troubleshooting**: See the Troubleshooting section above


---

## �📖 Citation

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
