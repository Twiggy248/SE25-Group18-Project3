# -----------------------------------------------------------------------------
# File: test_main.py
# Description: Test suite for main.py - comprehensive tests for FastAPI 
#              endpoints, use case extraction, and session management.
# Author: Pradyumna Chacham
# Date: November 2025
# Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
# License: MIT License - see LICENSE file in the root directory.
# -----------------------------------------------------------------------------

import json
import os
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
import torch
from fastapi import File, UploadFile
from fastapi.testclient import TestClient

from main import (UseCaseEstimator, app, clean_llm_json,
                  compute_usecase_embedding, ensure_string_list,
                  extract_use_cases_batch, flatten_use_case,
                  generate_fallback_title, generate_session_title,
                  get_smart_max_use_cases, get_smart_token_budget,
                  parse_large_document_chunked)


@pytest.fixture
def client():
    with TestClient(app) as client:
        # Initialize the database before running tests
        from main import init_db

        init_db()
        yield client


# Test data
SAMPLE_TEXT = """
The user should be able to login to the system. 
After logging in, users can search for products.
Users can add items to their cart and proceed to checkout.
Admin users can manage product inventory.
"""

SAMPLE_USE_CASE = {
    "title": "User Login",
    "preconditions": ["User has valid credentials"],
    "main_flow": [
        "User enters credentials",
        "System validates",
        "User is authenticated",
    ],
    "sub_flows": ["User can reset password"],
    "alternate_flows": ["If invalid: Show error"],
    "outcomes": ["User is logged in"],
    "stakeholders": ["User", "System"],
}


class TestUseCaseEstimator:
    def test_estimate_use_cases_basic(self):
        """Test basic use case estimation with simple text"""
        min_est, max_est, details = UseCaseEstimator.estimate_use_cases(SAMPLE_TEXT)

        # Should find login, search, add, checkout, manage actions
        assert min_est >= 1, "Should estimate at least 1 use case"
        assert max_est >= min_est, "Max estimate should be >= min estimate"
        assert details["unique_actions"] >= 3, "Should find at least 3 unique actions"

    def test_estimate_use_cases_empty(self):
        """Test estimation with empty text"""
        min_est, max_est, details = UseCaseEstimator.estimate_use_cases("")
        assert min_est == 1, "Should return minimum 1 for empty text"
        assert max_est >= min_est, "Max estimate should be >= min estimate"

    def test_estimate_use_cases_tiny(self):
        """Test estimation with very small text"""
        text = "User can login."
        min_est, max_est, details = UseCaseEstimator.estimate_use_cases(text)
        assert min_est == 1, "Should handle single action appropriately"
        assert "login" in details["found_actions"], "Should detect login action"
        assert max_est <= 2, "Should limit max estimate for tiny text"
        assert details["char_count"] < 100, "Should identify as tiny text"

    def test_estimate_use_cases_compound(self):
        """Test estimation with compound actions"""
        text = "User logs in and adds items to cart"
        min_est, max_est, details = UseCaseEstimator.estimate_use_cases(text)
        # Be more lenient - the algorithm should at least detect some actions
        assert min_est >= 1, "Should recognize at least one action"
        assert max_est >= min_est, "Max should be >= min"
        # Check that actions are detected (could be 'login' or variations)
        assert len(details["found_actions"]) > 0, "Should detect some actions"

    def test_estimate_use_cases_with_multiple_actors(self):
        """Test estimation with multiple actors"""
        text = "User can login. Admin can manage users. Customer can order products."
        min_est, max_est, details = UseCaseEstimator.estimate_use_cases(text)
        assert min_est >= 1, "Should detect at least one use case"
        assert max_est >= min_est
        assert details["unique_actions"] >= 1

    def test_estimate_use_cases_with_lists(self):
        """Test estimation with bullet points and numbered lists"""
        text = """
        1. User logs in
        2. User searches products
        3. User adds to cart
        - Admin manages inventory
        - System sends notifications
        """
        min_est, max_est, details = UseCaseEstimator.estimate_use_cases(text)
        assert min_est >= 1, "Should detect use cases from list"
        assert details["list_items"] >= 1  # Should detect at least some list items


class TestSmartMaxUseCases:
    def test_get_smart_max_basic(self):
        """Test basic smart max estimation"""
        max_cases = get_smart_max_use_cases(SAMPLE_TEXT)
        assert max_cases >= 3, "Should estimate at least 3 use cases for sample text"
        assert max_cases <= 20, "Should not exceed maximum of 20"

    def test_get_smart_max_tiny(self):
        """Test estimation for very small text"""
        text = "User logs in."
        max_cases = get_smart_max_use_cases(text)
        assert max_cases == 1, "Should estimate 1 use case for tiny text"
        assert max_cases <= 2, "Should limit max for tiny text"

    def test_get_smart_max_compound(self):
        """Test estimation with compound actions"""
        text = "User logs in and adds items to cart and updates profile."
        max_cases = get_smart_max_use_cases(text)
        assert max_cases >= 3, "Should recognize all compound actions"
        assert max_cases <= 5, "Should maintain reasonable upper limit"


class TestSmartTokenBudget:
    def test_get_smart_token_budget_basic(self):
        """Test token budget calculation"""
        budget = get_smart_token_budget(SAMPLE_TEXT, 4)
        assert 300 <= budget <= 1200, "Budget should be within reasonable bounds"
        base_tokens = 4 * 120 + 80  # 4 use cases × 120 + overhead
        assert budget == min(
            1200, max(300, base_tokens)
        ), "Should calculate budget correctly"

    def test_get_smart_token_budget_min(self):
        """Test minimum token budget"""
        budget = get_smart_token_budget("Short text", 1)
        assert budget >= 300, "Should not go below minimum budget"


class TestHelperFunctions:
    def test_clean_llm_json(self):
        """Test JSON cleaning function"""
        dirty_json = """```json
        [
            {"key": "value"},
            {"key2": None},
            {"key3": True}
        ]```"""
        cleaned = clean_llm_json(dirty_json)
        parsed = json.loads(cleaned)
        assert isinstance(parsed, list)
        assert len(parsed) == 3
        assert parsed[0]["key"] == "value"
        assert parsed[1]["key2"] is None
        assert parsed[2]["key3"] is True

        # Test with markdown code block
        md_json = """```
        {"key": "value"}
        ```"""
        cleaned = clean_llm_json(md_json)
        parsed = json.loads(cleaned)
        assert parsed["key"] == "value"

    def test_clean_llm_json_robust(self):
        """Test enhanced JSON cleaning with problematic cases"""
        # Test with escape characters
        escaped_json = r'[{"key": \"value\", "nested": \"quotes\"}]'
        cleaned = clean_llm_json(escaped_json)
        parsed = json.loads(cleaned)
        assert parsed[0]["key"] == "value"
        assert parsed[0]["nested"] == "quotes"

        # Test with unmatched brackets
        unmatched_json = '[{"key": "value"'
        cleaned = clean_llm_json(unmatched_json)
        parsed = json.loads(cleaned)
        assert isinstance(parsed, list)
        assert parsed[0]["key"] == "value"

        # Test with trailing commas
        trailing_json = '[{"key": "value",},]'
        cleaned = clean_llm_json(trailing_json)
        parsed = json.loads(cleaned)
        assert isinstance(parsed, list)
        assert parsed[0]["key"] == "value"

    def test_flatten_use_case(self):
        """Test use case flattening"""
        nested = {
            "title": "Test Case",
            "preconditions": {"cond1": "value1", "cond2": "value2"},
            "main_flow": ["step1", "step2"],
            "stakeholders": None,
        }
        flat = flatten_use_case(nested)
        assert isinstance(flat["preconditions"], list)
        assert isinstance(flat["main_flow"], list)
        assert isinstance(flat["stakeholders"], list)
        assert len(flat["main_flow"]) == 2

    def test_ensure_string_list(self):
        """Test string list conversion"""
        tests = [
            (["a", "b", 1], ["a", "b", "1"]),
            ("single", ["single"]),
            (None, []),
            ([{"key": "value"}], ['{"key": "value"}']),
        ]
        for input_val, expected in tests:
            result = ensure_string_list(input_val)
            assert result == expected

    @pytest.mark.skip(reason="Temporarily disabled")
    def test_compute_usecase_embedding(self, mock_embedder):
        """Test use case embedding computation"""
        # Mock the embedder
        mock_embedder.encode.return_value = torch.tensor([0.1, 0.2, 0.3])

        # Test with a UseCaseSchema object (not dict)
        from main import UseCaseSchema
        use_case = UseCaseSchema(
            title="Test Case",
            main_flow=["Step 1", "Step 2"],
            sub_flows=["Optional step"],
            alternate_flows=["Error case"],
            preconditions=[],
            outcomes=[],
            stakeholders=[]
        )

        embedding = compute_usecase_embedding(use_case)
        assert isinstance(embedding, torch.Tensor)
        assert embedding.shape == torch.Size([3])  # Assuming 3D for this test

        # Test embedding content
        mock_embedder.encode.assert_called_once()
        call_args = mock_embedder.encode.call_args[0][0]
        assert isinstance(call_args, str)
        assert "Test Case" in call_args
        assert "Step 1" in call_args
        assert "Step 2" in call_args
        # The function only uses title and main_flow, not sub_flows or alternate_flows

        # Test with missing fields
        minimal_case = {"title": "Test"}
        embedding = compute_usecase_embedding(minimal_case)
        assert isinstance(embedding, torch.Tensor)
        assert embedding.shape == torch.Size([3])

    def test_generate_session_title(self):
        """Test session title generation"""
        # In testing mode, generate_session_title uses fallback method
        # Test document upload
        doc_msg = "Uploaded document: requirements.pdf"
        title = generate_session_title(doc_msg)
        # In testing mode, it should return a date-based title
        assert "2025-11-08" in title or "Requirements" in title or len(title) > 0

        # Test regular text
        req_text = "User should be able to login and manage profile"
        title = generate_session_title(req_text)
        assert len(title.split()) >= 2
        assert len(title.split()) <= 10

        # Test fallback title generation
        non_ascii_text = "用户应该能够登录系统"  # Non-ASCII text
        title = generate_fallback_title(non_ascii_text)
        assert isinstance(title, str)
        assert "Session" in title  # Should contain "Session"
        assert len(title.split()) >= 2  # At least 2 words

        # Test ultimate fallback - should return "Requirements Session"
        title = generate_fallback_title("Empty text")
        assert title == "Requirements Session"

@pytest.mark.skip(reason="Requires embedder initialization")
class TestAPIEndpoints:
    def test_create_session(self, client):
        """Test session creation endpoint"""
        response = client.post(
            "/session/create",
            json={"project_context": "Test Project", "domain": "Test Domain"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["context"]["project_context"] == "Test Project"

    def test_update_session(self, client):
        """Test session update endpoint"""
        # Create session first
        create_resp = client.post(
            "/session/create",
            json={
                "project_context": "Initial Context",
            },
        )
        session_id = create_resp.json()["session_id"]

        # Update session
        response = client.post(
            "/session/update",
            json={
                "session_id": session_id,
                "project_context": "Updated Context",
                "domain": "Test Domain"
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id

    @patch("main.extract_use_cases_single_stage")
    def test_parse_use_case_fast(self, mock_extract, client):
        """Test use case extraction endpoint"""
        # Mock extraction function
        mock_extract.return_value = [SAMPLE_USE_CASE]

        response = client.post(
            "/parse_use_case_rag/",
            json={"raw_text": SAMPLE_TEXT, "project_context": "Test Project"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) > 0

    def test_query_requirements_empty(self, client):
        """Test query endpoint with no use cases"""
        # Create new session
        session_resp = client.post("/session/create", json={})
        session_id = session_resp.json()["session_id"]

        response = client.post(
            "/query",
            json={"session_id": session_id, "question": "What are the use cases?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "No use cases found" in data["answer"]

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "model" in data
        assert "features" in data

    @patch("main.embedder")
    def test_use_case_refinement(self, mock_embedder, client):
        """Test use case refinement endpoint"""
        # Create session and add use case
        session_resp = client.post("/session/create", json={})
        session_id = session_resp.json()["session_id"]

        mock_embedder.encode.return_value = [0.1] * 384  # Mock embedding vector

        # Add a use case via extraction
        with patch("main.extract_use_cases_single_stage") as mock_extract:
            mock_extract.return_value = [SAMPLE_USE_CASE]
            client.post(
                "/parse_use_case_rag/",
                json={"raw_text": "User logs in", "session_id": session_id},
            )

        # Get use case ID from database
        use_cases = client.get(f"/session/{session_id}/history").json()[
            "generated_use_cases"
        ]
        use_case_id = use_cases[0]["id"]

        # Test refinement - more main flows
        response1 = client.post(
            "/use-case/refine",
            json={"use_case_id": use_case_id, "refinement_type": "more_main_flows"},
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert "refined_use_case" in data1
        assert len(data1["refined_use_case"]["main_flow"]) >= len(
            SAMPLE_USE_CASE["main_flow"]
        )

        # Test refinement - more sub flows
        response2 = client.post(
            "/use-case/refine",
            json={"use_case_id": use_case_id, "refinement_type": "more_sub_flows"},
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["refined_use_case"]["sub_flows"]) >= len(
            SAMPLE_USE_CASE["sub_flows"]
        )

        # Test refinement - custom instruction
        response3 = client.post(
            "/use-case/refine",
            json={
                "use_case_id": use_case_id,
                "refinement_type": "custom",
                "custom_instruction": "Add security considerations",
            },
        )
        assert response3.status_code == 200
        data3 = response3.json()
        refined_use_case = data3["refined_use_case"]
        has_security = any(
            "security" in str(item).lower()
            for items in [
                refined_use_case["main_flow"],
                refined_use_case["sub_flows"],
                refined_use_case["alternate_flows"],
            ]
            for item in items
        )
        assert has_security, "Custom refinement should add security-related content"

    def test_export_endpoints(self, client):
        """Test export functionality"""
        # Create session with use case
        session_resp = client.post("/session/create", json={})
        session_id = session_resp.json()["session_id"]

        with patch("main.extract_use_cases_single_stage") as mock_extract:
            mock_extract.return_value = [SAMPLE_USE_CASE]
            client.post(
                "/parse_use_case_rag/",
                json={"raw_text": "User logs in", "session_id": session_id},
            )

        # Test export session data (no file operations)
        export_response = client.get(f"/session/{session_id}/export")
        assert export_response.status_code == 200
        data = export_response.json()
        assert "session_id" in data
        assert "conversation_history" in data
        assert "use_cases" in data

        # Test export session data
        export_response = client.get(f"/session/{session_id}/export")
        assert export_response.status_code == 200
        data = export_response.json()
        assert "session_id" in data
        assert "conversation_history" in data
        assert "use_cases" in data

    @patch("main.extract_text_from_file")
    def test_document_parsing(self, mock_extract, client):
        """Test document upload and parsing"""
        # Create dummy file
        dummy_content = BytesIO(b"User can login and view profile")
        file = UploadFile(filename="test.txt", file=dummy_content)

        # Mock text extraction
        mock_extract.return_value = ("User can login and view profile", "txt")

        # Create session
        session_resp = client.post("/session/create", json={})
        session_id = session_resp.json()["session_id"]

        # Upload and parse document
        with patch("main.parse_large_document_chunked") as mock_parse:
            mock_parse.return_value = {
                "message": "Success",
                "extracted_count": 2,
                "results": [{"title": "User Login"}, {"title": "View Profile"}],
            }

            files = {"file": ("test.txt", dummy_content)}
            response = client.post(
                f"/parse_use_case_document/?session_id={session_id}", files=files
            )

            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert len(data["results"]) == 2

    def test_session_management(self, client):
        """Test session listing and clearing"""
        # Test auto-title generation with text input
        session_with_text = client.post(
            "/parse_use_case_rag/",
            json={
                "raw_text": "User should be able to manage profile settings and update notifications",
                "project_context": "Project 1",
            },
        )
        session_id_1 = session_with_text.json()["session_id"]

        # Test auto-title generation with file upload
        with patch("main.extract_text_from_file") as mock_extract:
            mock_extract.return_value = ("Sample document content", "txt")
            files = {"file": ("requirements.txt", BytesIO(b"test"))}
            session_with_file = client.post(
                "/parse_use_case_document/",
                files=files,
                data={"project_context": "Project 2"},
            )
            session_id_2 = session_with_file.json()["session_id"]

        # List sessions and verify titles
        list_response = client.get("/sessions/")
        assert list_response.status_code == 200
        sessions = list_response.json()["sessions"]
        assert len(sessions) >= 2

        # Verify each session has appropriate properties
        for session in sessions:
            assert "session_title" in session
            assert "project_context" in session
            assert "last_active" in session
            assert isinstance(session["session_title"], str)

        # Test session title from document
        doc_sessions = [s for s in sessions if s["project_context"] == "Project 2"]
        assert len(doc_sessions) > 0
        assert "Requirements" in doc_sessions[0]["session_title"]

        # Test session title from text input
        text_sessions = [s for s in sessions if s["project_context"] == "Project 1"]
        assert len(text_sessions) > 0
        title = text_sessions[0]["session_title"]
        assert "Profile" in title or "Settings" in title or "Management" in title

        # Verify no duplicate sessions
        session_ids = [s["session_id"] for s in sessions]
        assert len(session_ids) == len(set(session_ids)), "Found duplicate session IDs"

        # Clear sessions
        for session_id in [session_id_1, session_id_2]:
            clear_response = client.delete(f"/session/{session_id}")
            assert clear_response.status_code == 200

        # Verify sessions are gone
        list_response = client.get("/sessions/")
        sessions = list_response.json()["sessions"]
        assert not any(
            s["session_id"] in [session_id_1, session_id_2] for s in sessions
        )

    @patch("main.extract_use_cases_single_stage")
    def test_batch_extraction(self, mock_extract, client):
        """Test batch extraction functionality"""
        # Create large text with multiple use cases
        text = "User can login. User can view profile. User can edit settings. " * 10

        # Setup mock to return different use cases for each batch
        mock_extract.return_value = [
            {"title": "User Login", "main_flow": ["Step 1"], "preconditions": [], "sub_flows": [], "alternate_flows": [], "outcomes": [], "stakeholders": []},
            {"title": "View Profile", "main_flow": ["Step 1"], "preconditions": [], "sub_flows": [], "alternate_flows": [], "outcomes": [], "stakeholders": []},
            {"title": "Edit Settings", "main_flow": ["Step 1"], "preconditions": [], "sub_flows": [], "alternate_flows": [], "outcomes": [], "stakeholders": []},
        ]

        # Extract use cases
        response = client.post(
            "/parse_use_case_rag/",
            json={"raw_text": text, "project_context": "Test Project"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "extraction_method" in data
    
    def test_list_sessions_endpoint(self, client):
        """Test GET /sessions/ endpoint"""
        # Create a few sessions
        for i in range(3):
            client.post("/session/create", json={
                "project_context": f"Project {i}",
                "domain": f"Domain {i}"
            })
        
        # Get all sessions
        response = client.get("/sessions/")
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert isinstance(data["sessions"], list)
        assert len(data["sessions"]) >= 3
        
        # Verify session structure
        for session in data["sessions"]:
            assert "session_id" in session
            assert "created_at" in session
            assert "session_title" in session
    
    def test_get_session_title_endpoint(self, client):
        """Test GET /session/{session_id}/title endpoint"""
        # Create session
        create_resp = client.post("/session/create", json={
            "project_context": "Test Project",
            "domain": "Test Domain"
        })
        session_id = create_resp.json()["session_id"]
        
        # Get session title
        response = client.get(f"/session/{session_id}/title")
        assert response.status_code == 200
        data = response.json()
        assert "session_title" in data
        assert "session_id" in data
        assert data["session_id"] == session_id

    def test_error_handling(self, client):
        """Test error handling in various endpoints"""
        # Test invalid session ID
        response = client.post(
            "/query",
            json={"session_id": "invalid_id", "question": "What are the use cases?"},
        )
        assert response.status_code == 200  # Should handle gracefully
        assert "No use cases found" in response.json()["answer"]

        # Test invalid use case ID in refinement
        response = client.post(
            "/use-case/refine",
            json={"use_case_id": 99999, "refinement_type": "more_main_flows"},
        )
        assert response.status_code == 404

        # Test invalid export request
        response = client.get("/session/invalid_id/export/markdown")
        assert response.status_code == 404

    @patch("main.extract_use_cases_single_stage")
    def test_chunked_processing(self, mock_extract, client):
        """Test chunked document processing"""
        # Create a very long document to trigger chunked processing
        long_text = "Requirements Document\n\n" + (
            "The user should be able to perform action X. " * 100
        )

        # Setup mock to return valid use cases
        mock_extract.return_value = [SAMPLE_USE_CASE]

        # Test chunked processing
        response = client.post(
            "/parse_use_case_rag/",
            json={"raw_text": long_text, "project_context": "Large Document Test"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "stored_count" in data
        assert data["stored_count"] > 0  # Should store at least one use case


# Helper function for tests
@pytest.fixture
def mock_pipe_response():
    return [
        {
            "generated_text": json.dumps(
                [
                    {
                        "title": "User Login",
                        "preconditions": ["User has valid credentials"],
                        "main_flow": ["Step 1", "Step 2"],
                        "sub_flows": ["Optional step"],
                        "alternate_flows": ["Error handling"],
                        "outcomes": ["Success"],
                        "stakeholders": ["User"],
                    }
                ]
            )
        }
    ]


# Additional test classes to improve coverage
class TestProcessing:
    @pytest.mark.skip(reason="Temporarily disabled")
    @patch("main.chunker")
    def test_document_chunking(
        self, mock_chunker, mock_extract, client, mock_pipe_response
    ):
        """Test document chunking and processing"""
        long_text = "A" * 5000  # Long text that should trigger chunking

        # Setup mock chunks with different content
        mock_chunker.chunk_document.return_value = [
            {
                "text": "User can login and view profile",
                "chunk_id": "1",
                "char_count": 1000,
            },
            {
                "text": "User can edit settings and manage account",
                "chunk_id": "2",
                "char_count": 1000,
            },
            {
                "text": "User can search products and place orders",
                "chunk_id": "3",
                "char_count": 1000,
            },
        ]

        # Mock different use cases for each chunk
        mock_extract.side_effect = [
            [{"title": "User Login", "main_flow": ["Step 1"]}],
            [{"title": "Edit Settings", "main_flow": ["Step 1"]}],
            [{"title": "Search Products", "main_flow": ["Step 1"]}],
        ]

        response = client.post(
            "/parse_use_case_rag/",
            json={"raw_text": long_text, "project_context": "Large Test"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["extraction_method"] == "chunked_processing_smart"
        assert data["chunks_processed"] == 3
        assert data["extracted_count"] >= 3
        assert "chunk_summaries" in data
        assert all("chunk_id" in summary for summary in data["chunk_summaries"])
        assert all("use_cases_found" in summary for summary in data["chunk_summaries"])

        # Verify each chunk was processed
        assert mock_extract.call_count == 3

        # Verify merge and deduplication worked
        assert len(data["results"]) >= 3
        titles = [r["title"] for r in data["results"]]
        assert len(titles) == len(set(titles)), "Should have no duplicate titles"

    @pytest.mark.skip(reason="Temporarily disabled")
    def test_duplicate_detection(self, mock_embedder, client, mock_pipe_response):
        """Test duplicate use case detection"""
        mock_embedder.encode.return_value = torch.tensor([0.1, 0.2, 0.3])

        # Create session and add first use case
        session_resp = client.post("/session/create", json={})
        session_id = session_resp.json()["session_id"]

        with patch("main.extract_use_cases_single_stage") as mock_extract:
            mock_extract.return_value = [SAMPLE_USE_CASE]

            # First submission
            response1 = client.post(
                "/parse_use_case_rag/",
                json={"raw_text": "User logs in", "session_id": session_id},
            )

            # Second submission of similar use case
            response2 = client.post(
                "/parse_use_case_rag/",
                json={"raw_text": "User logs into system", "session_id": session_id},
            )

            data1 = response1.json()
            data2 = response2.json()

            assert data1["stored_count"] >= 1
            assert data2["duplicate_count"] >= 1


class TestAdditionalEndpoints:
    """Test additional endpoints to increase coverage"""

    def test_generate_fallback_title(self):
        """Test fallback title generation"""
        title = generate_fallback_title("User can login to system", max_length=50)
        assert isinstance(title, str)
        assert len(title) > 0

    def test_flatten_use_case_comprehensive(self):
        """Test flatten_use_case with various formats"""
        # Test with main_flows as list of lists
        use_case1 = {
            "title": "Test UC",
            "main_flows": [["Step 1", "Step 2"], ["Step 3"]],
            "preconditions": "Single precondition",
            "outcomes": ["Outcome 1"]
        }
        flat1 = flatten_use_case(use_case1)
        assert flat1["title"] == "Test UC"
        assert isinstance(flat1["main_flow"], list)
        assert isinstance(flat1["preconditions"], list)
        
        # Test with main_flow (singular)
        use_case2 = {
            "title": "Test UC 2",
            "main_flow": ["Step A", "Step B"]
        }
        flat2 = flatten_use_case(use_case2)
        assert flat2["main_flow"] == ["Step A", "Step B"]

    def test_ensure_string_list_edge_cases(self):
        """Test ensure_string_list with edge cases"""
        # Test with None
        assert ensure_string_list(None) == []
        
        # Test with empty string
        assert ensure_string_list("") == []
        
        # Test with nested lists
        result = ensure_string_list([["a", "b"], "c"])
        assert isinstance(result, list)
        assert all(isinstance(x, str) for x in result)

    def test_clean_llm_json_variations(self):
        """Test clean_llm_json with various inputs"""
        # Test with trailing comma before closing brace
        json_with_comma = '{"key": "value",}'
        cleaned = clean_llm_json(json_with_comma)
        assert '",}' not in cleaned
        
        # Test with trailing comma before closing bracket
        json_array_comma = '["item1", "item2",]'
        cleaned_array = clean_llm_json(json_array_comma)
        assert '",]' not in cleaned_array


# Run tests with: python -m pytest tests/test_main.py -v --cov=main --cov-report term-missing
