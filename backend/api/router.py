from fastapi import Request, HTTPException, APIRouter
from routers import api_session, api_user, api_parse
from database.models import RefinementRequest, QueryRequest
from database.managers import usecase_db_manager
import main, json, re
import managers.query_manager as query
from security import require_user, session_belongs_to_user
router = APIRouter()

router.include_router(api_session.router)
router.include_router(api_user.router)
router.include_router(api_parse.router)

@router.post("/use-case/refine")
def refine_use_case_endpoint(request: RefinementRequest):
    """Refine a specific use case based on user request"""

    use_case = usecase_db_manager.get_use_case_by_id(request.use_case_id)
    if not use_case:
        raise HTTPException(status_code=404, detail="Use case not found")

    # Build refinement prompt based on type
    prompt = query.refineQueryGeneration(use_case, request.refinement_type)

    try:
        outputs = main.pipe(
            prompt,
            max_new_tokens=800,
            temperature=0.4,
            top_p=0.9,
            do_sample=True,
            return_full_text=False,
        )

        response = outputs[0]["generated_text"].strip()

        # Extract JSON
        if not response.startswith("{"):
            response = "{" + response

        start = response.find("{")
        end = response.rfind("}")

        if start != -1 and end != -1:
            json_str = response[start : end + 1]
            json_str = re.sub(r",(\s*[}\]])", r"\1", json_str)
            refined = json.loads(json_str)

            # Update in database
            usecase_db_manager.update_use_case(request.use_case_id, refined)

            return {"message": "Use case refined successfully",
                    "refined_use_case": refined}
        else:
            raise ValueError("Could not extract valid JSON from refinement")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")

@router.post("/query")
def query_requirements(request: QueryRequest, request_data: Request):
    """Answer natural language questions about requirements"""

    user_id = require_user(request_data)
    session_id = request.session_id

    if not session_belongs_to_user(session_id, user_id):
        raise HTTPException(403, "Forbidden")


    use_cases = usecase_db_manager.get_use_case_by_session(request.session_id)

    if not use_cases:
        return {
            "answer": "No use cases found for this session yet.",
            "relevant_use_cases": [],
        }

    # Remove database IDs from use cases before sending to LLM
    # This prevents use case numbers from appearing in explanations
    use_cases_for_context = []
    for uc in use_cases:
        use_case_without_id = {
            "title": uc.get("title", ""),
            "preconditions": uc.get("preconditions", []),
            "main_flow": uc.get("main_flow", []),
            "sub_flows": uc.get("sub_flows", []),
            "alternate_flows": uc.get("alternate_flows", []),
            "outcomes": uc.get("outcomes", []),
            "stakeholders": uc.get("stakeholders", []),
        }
        use_cases_for_context.append(use_case_without_id)

    context = json.dumps(use_cases_for_context, indent=2)

    prompt = query.requirementsQueryGeneration(context, request.question)

    try:
        outputs = main.pipe(
            prompt,
            max_new_tokens=400,
            temperature=0.5,
            top_p=0.9,
            do_sample=True,
            return_full_text=False,
        )

        answer = outputs[0]["generated_text"].strip()

        # Post-process to remove any use case numbers that might have slipped through
        # Remove patterns like "Use Case 249", "Use Case 248", "UC 253", etc.
        answer = re.sub(r"\(Use Case\s+\d+\)", "", answer, flags=re.IGNORECASE)
        answer = re.sub(r"\(Use Cases\s+\d+[,\s]*\d*\)", "", answer, flags=re.IGNORECASE)
        answer = re.sub(r"Use Case\s+\d+", "", answer, flags=re.IGNORECASE)
        answer = re.sub(r"UC\s+\d+", "", answer, flags=re.IGNORECASE)
        # Clean up any double spaces or trailing commas/spaces
        answer = re.sub(r"\s+", " ", answer)
        answer = re.sub(r"\s*,\s*,", ",", answer)
        answer = re.sub(r"\s*,\s*\.", ".", answer)
        answer = answer.strip()

        # Find relevant use cases
        question_lower = request.question.lower()
        relevant = []

        for uc in use_cases:
            if any(word in uc["title"].lower() for word in question_lower.split()):
                relevant.append(uc["title"])

        return {
            "answer": answer,
            "relevant_use_cases": relevant,
            "total_use_cases": len(use_cases),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


# NOTE: Why have this if it is hardcoded?
@router.get("/health")
def health_check():
    """Health check endpoint with system info"""
    return {
        "status": "healthy",
        "model": main.MODEL_NAME,
        "extraction_method": "smart_single_stage_with_chunking",
        "performance": "Intelligent estimation + dynamic token budgets",
        "features": [
            "✅ Smart use case estimation (no hardcoded limits!)",
            "✅ Dynamic token budgeting (300-1500 tokens)",
            "✅ Action verb detection and analysis",
            "✅ Document upload (PDF, DOCX, TXT, MD)",
            "✅ Intelligent chunking for large documents",
            "✅ Automatic size detection and processing strategy",
            "✅ Smart fallback with pattern matching",
            "✅ Automatic quality validation",
            "✅ Duplicate detection with embeddings",
            "✅ Session management",
            "✅ Conversation memory",
            "✅ Conflict detection",
            "✅ Quality metrics",
            "✅ Multiple export formats (DOCX, PlantUML, Markdown)",
            "✅ Natural language queries",
            "✅ Interactive refinement",
        ],
        "supported_formats": ["PDF", "DOCX", "TXT", "MD"],
        "max_file_size": "10MB",
        "chunking": {
            "enabled": True,
            "max_tokens_per_chunk": 3000,
            "strategies": ["auto", "section", "paragraph", "sentence"],
        },
        "smart_estimation": {
            "enabled": True,
            "analyzes": ["action_verbs", "actors", "sentence_structure", "list_items"],
            "dynamic_token_budget": True,
            "no_hallucination": True,
        },
        "speed": "Optimized based on input size and complexity",
        "improvements_v2": {
            "smart_estimation": "Analyzes text to determine actual use case count",
            "no_hardcoded_limits": "No more hardcoded max_use_cases = 8",
            "dynamic_tokens": "Token budget adapts to estimated need (300-1500)",
            "no_hallucination": "LLM only generates what actually exists",
            "faster": "Reduced token generation for small inputs",
        },
    }

# NOTE: Why have this if it is hardcoded?
@router.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": "Requirements Engineering Tool API",
        "version": "4.0 - Smart Use Case Estimation",
        "description": "Converts unstructured requirements to structured use cases with intelligent estimation",
        "endpoints": {
            "extraction_text": "POST /parse_use_case_rag/",
            "extraction_document": "POST /parse_use_case_document/",
            "sessions": "POST /session/create, GET /sessions/",
            "history": "GET /session/{session_id}/history",
            "metrics": "GET /session/{session_id}/metrics",
            "query": "POST /query",
            "refine": "POST /use-case/refine",
            "conflicts": "GET /session/{session_id}/conflicts",
            "exports": "GET /session/{session_id}/export/{format}",
            "health": "GET /health",
        },
        "key_improvements": {
            "v4.0_smart_estimation": {
                "problem": "Previously hardcoded max_use_cases=8 caused hallucination",
                "solution": "Intelligent text analysis to estimate actual use case count",
                "benefits": [
                    "No more hallucinated use cases",
                    "Dynamic token budgets (300-1500 based on need)",
                    "Faster processing for small inputs",
                    "More accurate extraction",
                    "Analyzes: action verbs, actors, sentence structure, list items",
                ],
            },
            "document_upload": "Upload PDF, DOCX, TXT, MD files",
            "intelligent_chunking": "Automatic chunking for large documents",
            "size_detection": "Auto-detects text size and chooses best strategy",
            "quality": "Automatic validation and enrichment",
        },
        "usage_example": {
            "endpoint": "POST /parse_use_case_rag/",
            "body": {
                "raw_text": "User can login. User can search products.",
                "session_id": "optional-session-id",
                "project_context": "E-commerce Platform",
                "domain": "Online Retail",
            },
            "expected_result": {
                "extracted_count": 2,
                "processing_time": "2-5 seconds",
                "quality_scores": "High (no hallucination)",
                "message": "Smart extraction: 2 use cases (not 8!)",
            },
        },
    }
