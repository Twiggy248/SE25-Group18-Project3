# 🔌 API Documentation - ReqEngine

Complete REST API reference for the ReqEngine backend service.

**Base URL**: `http://localhost:8000`

---

## 📊 API Overview

### Core Endpoints
- **Use Case Extraction**: 2 endpoints
- **Session Management**: 6 endpoints  
- **Query System**: 1 endpoint
- **Use Case Operations**: 1 endpoint
- **System**: 2 endpoints

### Authentication
- **Hugging Face Token**: Required for LLM model access
- **API Access**: Currently open (no authentication required)

---

## 🚀 Use Case Extraction

### Extract from Text
Extract use cases from raw text input with intelligent processing.

```http
POST /parse_use_case_rag/
```

**Request Body:**
```json
{
  "raw_text": "Users must be able to login and search for products",
  "session_id": "optional-session-id",
  "project_context": "E-commerce Platform",
  "domain": "Retail"
}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "results": [
    {
      "id": 1,
      "title": "User Login",
      "preconditions": ["User has valid credentials"],
      "main_flow": [
        "User opens login page",
        "User enters credentials",
        "System validates credentials"
      ],
      "alternate_flows": ["If invalid: Show error message"],
      "outcomes": ["User is authenticated"],
      "stakeholders": ["User", "Authentication System"]
    }
  ],
  "extraction_metadata": {
    "estimated_use_cases": 2,
    "processing_time": 3.45,
    "model_used": "meta-llama/Llama-3.2-3B-Instruct"
  }
}
```

### Extract from Document
Extract use cases from uploaded files (PDF, DOCX, TXT, Markdown).

```http
POST /parse_use_case_document/
```

**Request (Multipart Form):**
```
file: [uploaded file]
session_id: "optional-session-id"
project_context: "Banking System"
domain: "Financial Services"
```

**Supported Formats:**
- PDF (`.pdf`)
- Microsoft Word (`.docx`)
- Plain Text (`.txt`)
- Markdown (`.md`)

**File Limits:**
- Maximum size: 50MB
- Text length: Up to 100,000 characters

---

## 🗂️ Session Management

### Create Session
Create a new requirements engineering session.

```http
POST /session/create
```

**Request:**
```json
{
  "session_id": "optional-custom-id",
  "project_context": "Healthcare Management System",
  "domain": "Healthcare"
}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "context": {
    "project_context": "Healthcare Management System",
    "domain": "Healthcare",
    "created_at": "2025-11-06T10:30:00Z"
  },
  "message": "Session created successfully"
}
```

### Update Session
Update existing session context and metadata.

```http
POST /session/update
```

**Request:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_context": "Updated Healthcare System",
  "domain": "Digital Health"
}
```

### List All Sessions
Get all available sessions with metadata.

```http
GET /sessions/
```

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "session_title": "Healthcare Management System",
      "project_context": "Healthcare Management System",
      "domain": "Healthcare",
      "created_at": "2025-11-06T10:30:00Z",
      "last_active": "2025-11-06T11:45:00Z"
    }
  ]
}
```

### Get Session History
Retrieve conversation history for a specific session.

```http
GET /session/{session_id}/history?limit=10
```

**Parameters:**
- `session_id`: UUID of the session
- `limit`: Number of messages to retrieve (default: 10)

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "history": [
    {
      "id": 1,
      "role": "user",
      "content": "Extract use cases from uploaded document",
      "timestamp": "2025-11-06T10:35:00Z",
      "metadata": {"file_name": "requirements.pdf"}
    },
    {
      "id": 2,
      "role": "assistant", 
      "content": "Successfully extracted 5 use cases",
      "timestamp": "2025-11-06T10:35:15Z"
    }
  ]
}
```

### Export Session
Export all session data in various formats.

```http
GET /session/{session_id}/export
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "conversation_history": [...],
  "context": {...},
  "use_cases": [...],
  "summary": {...},
  "export_timestamp": "2025-11-06T12:00:00Z"
}
```

### Delete Session
Remove a session and all associated data.

```http
DELETE /session/{session_id}
```

**Response:**
```json
{
  "message": "Session 550e8400-e29b-41d4-a716-446655440000 deleted successfully"
}
```

---

## 🔧 Use Case Operations

### Refine Use Case
Improve specific components of an extracted use case.

```http
POST /use-case/refine
```

**Request:**
```json
{
  "use_case_id": 123,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "refinement_type": "more_alternate_flows",
  "additional_context": "Consider error scenarios and edge cases"
}
```

**Refinement Types:**
- `more_main_flows`: Add detailed main flow steps
- `more_alternate_flows`: Add alternative and exception flows
- `more_preconditions`: Add detailed preconditions
- `improve_outcomes`: Enhance outcome descriptions

**Response:**
```json
{
  "use_case_id": 123,
  "updated_fields": {
    "alternate_flows": [
      "If user account is locked: Display account locked message",
      "If password expired: Redirect to password reset",
      "If system maintenance: Show maintenance notice"
    ]
  },
  "refinement_metadata": {
    "refinement_type": "more_alternate_flows",
    "processing_time": 2.1
  }
}
```

---

## 🔍 Query System

### Natural Language Query
Ask questions about extracted use cases using natural language.

```http
POST /query
```

**Request:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "question": "What are the main actors in the login process?",
  "max_results": 5
}
```

**Response:**
```json
{
  "question": "What are the main actors in the login process?",
  "answer": "The main actors in the login process are User and Authentication System.",
  "relevant_use_cases": [
    {
      "use_case_id": 1,
      "title": "User Login",
      "relevance_score": 0.95,
      "matching_sections": ["stakeholders", "main_flow"]
    }
  ],
  "sources": [
    {
      "use_case_id": 1,
      "excerpt": "Stakeholders: User, Authentication System"
    }
  ]
}
```

---

## 🔧 System Endpoints

### Health Check
Verify service status and dependencies.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-06T12:00:00Z",
  "version": "1.0.0",
  "dependencies": {
    "database": "connected",
    "llm_model": "loaded",
    "vector_store": "available"
  }
}
```

### API Information
Get API version and available endpoints.

```http
GET /
```

**Response:**
```json
{
  "name": "ReqEngine API",
  "version": "1.0.0",
  "description": "Intelligent Requirements Engineering Tool",
  "documentation": "/docs",
  "endpoints": 12,
  "features": [
    "Use case extraction",
    "Semantic search",
    "Multi-format document processing",
    "Interactive refinement"
  ]
}
```

---

## 📝 Request/Response Formats

### Standard Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Raw text cannot be empty",
    "details": {
      "field": "raw_text",
      "value": "",
      "constraint": "non_empty"
    }
  },
  "timestamp": "2025-11-06T12:00:00Z",
  "request_id": "req_123456789"
}
```

### Common HTTP Status Codes
- `200`: Success
- `201`: Created (new session)
- `400`: Bad Request (validation error)
- `404`: Not Found (session/use case not found)
- `422`: Unprocessable Entity (invalid input format)
- `500`: Internal Server Error

---

## 🚀 Usage Examples

### Python Client Example
```python
import requests

# Create session and extract use cases
api_base = "http://localhost:8000"

# Create session
session_response = requests.post(f"{api_base}/session/create", json={
    "project_context": "E-commerce Platform",
    "domain": "Retail"
})
session_id = session_response.json()["session_id"]

# Extract use cases
extraction_response = requests.post(f"{api_base}/parse_use_case_rag/", json={
    "raw_text": "Users must login and search products",
    "session_id": session_id
})

use_cases = extraction_response.json()["results"]
print(f"Extracted {len(use_cases)} use cases")
```

### JavaScript/Fetch Example
```javascript
// Extract use cases from text
const extractUseCases = async (text, sessionId) => {
  const response = await fetch('http://localhost:8000/parse_use_case_rag/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      raw_text: text,
      session_id: sessionId,
      project_context: 'Web Application',
      domain: 'Technology'
    })
  });
  
  return await response.json();
};

// Query use cases
const queryUseCases = async (question, sessionId) => {
  const response = await fetch('http://localhost:8000/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question: question,
      session_id: sessionId,
      max_results: 5
    })
  });
  
  return await response.json();
};
```

---

## 🔧 Rate Limits & Performance

### Current Limits
- **No rate limiting** implemented (development version)
- **File size**: 50MB maximum
- **Text length**: 100,000 characters maximum
- **Concurrent requests**: Limited by system resources

### Performance Expectations
- **Text extraction**: 2-5 seconds for typical requirements
- **Document processing**: 5-15 seconds depending on size
- **Query response**: <1 second for semantic search
- **Session operations**: <500ms for CRUD operations

### Optimization Tips
- Use session IDs to maintain context efficiently
- Break large documents into smaller chunks
- Utilize the smart estimation feature for better performance
- Cache frequently accessed sessions

---

For implementation details, see the [backend README](../backend/README.md).  
For setup instructions, see [INSTALL.md](INSTALL.md).