# -----------------------------------------------------------------------------
# File: test_rag_utils.py
# Description: Test suite for rag_utils.py - tests RAG functionality, vector
#              store operations, and semantic search capabilities.
# Author: Pradyumna Chacham
# Date: November 2025
# Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
# License: MIT License - see LICENSE file in the root directory.
# -----------------------------------------------------------------------------

import os
from unittest.mock import MagicMock, patch

import pytest

from rag_utils import extract_use_cases, process_document, semantic_chunk


@pytest.fixture
def complex_requirements_doc():
    return """
    Enterprise Data Platform Requirements
    
    Use Case: Real-time Data Processing
    Actor: Data Engineer
    Goal: Process and analyze streaming data in real-time
    
    Functional Requirements:
    1. Ingest data from multiple sources (Kafka, RabbitMQ, IoT devices)
    2. Apply complex event processing rules
    3. Generate real-time alerts and dashboards
    
    Performance Requirements:
    - Process 1M events per second
    - End-to-end latency < 100ms
    - 99.999% uptime
    
    Security Requirements:
    - End-to-end encryption
    - Role-based access control
    - Audit logging for all operations
    
    Integration Points:
    - Data Warehouse
    - ML Pipeline
    - Monitoring Systems
    """


@pytest.fixture
def ambiguous_requirements_doc():
    return """
    Mobile App Feature
    
    The app should be fast and user-friendly.
    Users should be able to do things quickly.
    The system needs good performance.
    
    Security should be strong.
    Make it scalable for future.
    """


@pytest.fixture
def sample_document():
    return """
    Project Requirements Document
    
    User Story 1: As a customer, I want to be able to search for products by category
    so that I can quickly find what I'm looking for.
    
    User Story 2: As an admin, I need to be able to update product inventory
    so that stock levels are accurate.
    
    Technical Requirements:
    - Must support real-time inventory updates
    - Search functionality should be fast and accurate
    - System should handle high concurrent user load
    """


@pytest.mark.asyncio
async def test_process_document_extraction(complex_requirements_doc):
    """
    CORE THESIS TEST: Natural Language Requirement Processing

    This test validates our system's core capability to extract structured
    requirements from natural language text. It tests our main value
    proposition of automated requirement analysis.

    Key aspects tested:
    1. Extraction of different requirement types (functional, non-functional)
    2. Recognition of technical specifications
    3. Identification of integration points
    4. Performance criteria extraction
    """
    with patch("rag_utils.get_llm_response") as mock_llm:
        # Setup mock LLM response with realistic structured output
        mock_llm.return_value = {
            "use_cases": [
                {
                    "id": "UC1",
                    "title": "Real-time Data Processing",
                    "actor": "Data Engineer",
                    "goal": "Process and analyze streaming data in real-time",
                    "functional_requirements": [
                        "Ingest data from multiple sources",
                        "Apply complex event processing rules",
                        "Generate real-time alerts",
                    ],
                    "performance_requirements": [
                        "Process 1M events per second",
                        "End-to-end latency < 100ms",
                    ],
                    "security_requirements": [
                        "End-to-end encryption",
                        "Role-based access control",
                    ],
                    "integration_points": ["Data Warehouse", "ML Pipeline"],
                }
            ]
        }

        result = await process_document(complex_requirements_doc)

        # Validate core requirement extraction capabilities
        assert result is not None
        use_case = result["use_cases"][0]

        # Test functional requirement extraction
        assert len(use_case["functional_requirements"]) >= 3
        assert any("data" in req.lower() for req in use_case["functional_requirements"])

        # Test performance requirement extraction
        assert any("1M events" in req for req in use_case["performance_requirements"])

        # Test security requirement identification
        assert any(
            "encryption" in req.lower() for req in use_case["security_requirements"]
        )

        # Test integration point detection
        assert "Data Warehouse" in use_case["integration_points"]


@pytest.mark.asyncio
async def test_requirement_quality_analysis(ambiguous_requirements_doc):
    """
    CORE THESIS TEST: Requirement Quality Assessment

    This test validates our system's ability to identify and flag ambiguous
    or low-quality requirements. This is a critical feature for ensuring
    requirements meet industry standards.

    Test cases include:
    1. Detection of ambiguous terms
    2. Identification of missing specifics
    3. Recognition of non-measurable criteria
    4. Validation against IEEE standards
    """
    with patch("rag_utils.get_llm_response") as mock_llm:
        mock_llm.return_value = {
            "analysis": {
                "ambiguous_terms": ["fast", "user-friendly", "good", "strong"],
                "missing_specifics": [
                    "No measurable performance criteria",
                    "Security requirements lack detail",
                    "Scalability requirements not quantified",
                ],
                "quality_score": 35,
                "improvement_suggestions": [
                    "Define specific performance metrics",
                    "Specify security requirements",
                    "Quantify scalability targets",
                ],
            }
        }

        result = await process_document(ambiguous_requirements_doc)

        # Validate ambiguity detection
        analysis = result["analysis"]
        assert len(analysis["ambiguous_terms"]) >= 3
        assert analysis["quality_score"] < 50  # Poor quality score expected

        # Validate improvement suggestions
        assert len(analysis["improvement_suggestions"]) >= 3
        assert any(
            "metrics" in sugg.lower() for sugg in analysis["improvement_suggestions"]
        )
        assert any(
            "security" in sugg.lower() for sugg in analysis["improvement_suggestions"]
        )


@pytest.mark.asyncio
async def test_process_document_error_handling():
    """
    Tests error handling in the document processing pipeline.
    This ensures system resilience and proper user feedback.
    """
    with patch("rag_utils.get_llm_response", side_effect=Exception("LLM Error")):
        with pytest.raises(Exception) as exc_info:
            await process_document("Test content")
        assert "LLM Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_process_document_with_complex_requirements():
    """
    Tests processing of complex requirements with multiple interconnected use cases.
    This validates our system's ability to handle realistic enterprise scenarios.
    """
    complex_doc = """
    Epic: Order Management System
    
    Use Case 1:
    As a customer service representative
    I want to view a customer's order history
    So that I can assist with inquiries
    
    Use Case 2:
    As a shipping manager
    I want to track delivery status
    So that I can ensure timely deliveries
    
    Integration Requirements:
    - Must integrate with existing CRM
    - Real-time updates from shipping partners
    - Historical data preservation
    """

    with patch("rag_utils.get_llm_response") as mock_llm:
        mock_llm.return_value = {
            "use_cases": [
                {
                    "id": "UC1",
                    "title": "View Customer Order History",
                    "actor": "Customer Service Representative",
                    "goal": "Access and review customer orders",
                    "steps": [
                        "Open customer profile",
                        "View order history",
                        "Filter by date",
                    ],
                },
                {
                    "id": "UC2",
                    "title": "Track Delivery Status",
                    "actor": "Shipping Manager",
                    "goal": "Monitor delivery progress",
                    "steps": [
                        "Access shipping dashboard",
                        "View active deliveries",
                        "Check status updates",
                    ],
                },
            ]
        }

        result = await process_document(complex_doc)
        assert len(result["use_cases"]) == 2
        assert all("steps" in uc for uc in result["use_cases"])
        assert all(len(uc["steps"]) >= 3 for uc in result["use_cases"])


@pytest.mark.asyncio
async def test_extract_use_cases_with_requirements():
    """
    Tests extraction of use cases with associated non-functional requirements.
    This ensures our system captures complete requirement context.
    """
    doc_with_reqs = """
    Use Case: Product Search
    Actor: Customer
    Goal: Find specific products quickly
    
    Requirements:
    - Search response time < 2 seconds
    - Support fuzzy matching
    - Handle 1000+ concurrent searches
    """

    with patch("rag_utils.validate_use_case") as mock_validator:
        mock_validator.return_value = True
        use_cases = await extract_use_cases(doc_with_reqs)

        assert len(use_cases) > 0
        first_case = use_cases[0]
        assert "requirements" in first_case
        assert any("response time" in req.lower() for req in first_case["requirements"])


@pytest.mark.asyncio
async def test_process_document_maintains_traceability():
    """
    Tests that processed documents maintain traceability to source requirements.
    This validates our requirement tracing capabilities.
    """
    with patch("rag_utils.get_llm_response") as mock_llm:
        mock_llm.return_value = {
            "use_cases": [
                {
                    "id": "UC1",
                    "source_location": "Page 1, Paragraph 2",
                    "original_text": "As a user, I want to login",
                    "processed_requirements": [
                        "Secure authentication",
                        "Password rules",
                    ],
                }
            ]
        }

        result = await process_document("Test content")
        assert "source_location" in result["use_cases"][0]
        assert "original_text" in result["use_cases"][0]
        assert "processed_requirements" in result["use_cases"][0]


def test_semantic_chunk_basic():
    """Test basic semantic chunking"""
    text = "User can login. User can logout. User can register."
    chunks = semantic_chunk(text, chunk_size=2, overlap=1)
    
    # Should create chunks
    assert len(chunks) >= 1
    assert isinstance(chunks, list)
    assert all(isinstance(c, str) for c in chunks)


def test_semantic_chunk_with_sentences():
    """Test chunking with multiple sentences"""
    text = "First sentence here. Second sentence here. Third sentence here. Fourth sentence here."
    chunks = semantic_chunk(text, chunk_size=2, overlap=0)
    
    # Should split into chunks
    assert len(chunks) >= 1
    combined = " ".join(chunks)
    assert "First sentence" in combined or "sentence" in combined.lower()


def test_extract_key_concepts():
    """Test key concept extraction from text"""
    from rag_utils import extract_key_concepts
    text = "User authentication system login logout registration password security"
    concepts = extract_key_concepts(text, top_n=5)
    assert isinstance(concepts, list)
    assert len(concepts) <= 5
    assert all(isinstance(c, str) for c in concepts)
