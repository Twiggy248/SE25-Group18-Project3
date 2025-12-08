import json
import re
from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ..security import require_user
from ...database.managers import session_db_manager, usecase_db_manager
from ...managers.llm_manager import makeQuery

"""
api_summarize.py
Handles summarization of chat sessions and use cases
"""

router = APIRouter(
    prefix="/summarize",
    tags=["summarize"],
)


class ChatMessage(BaseModel):
    role: str
    content: str
    use_cases: list


class SummarizeRequest(BaseModel):
    messages: list[ChatMessage]


class UseCaseSummary(BaseModel):
    title: str
    summary: str


class SummaryResponse(BaseModel):
    main_summary: str
    use_case_summaries: list[UseCaseSummary]


def clean_llm_response(text: str) -> str:
    """
    Remove common LLM preamble and fluff from responses.
    """
    # List of patterns to remove (case-insensitive)
    patterns_to_remove = [
        r"^(sure!?\s*)?here'?s?\s+(a\s+)?(the\s+)?summary:?\s*",
        r"^(sure!?\s*)?here'?s?\s+(my\s+)?(the\s+)?response:?\s*",
        r"^thank you for (providing|asking|the)\s+.*?\.\s*",
        r"^i hope this (summary|response) meets your requirements!?\s*",
        r"^let me know if (i can help|you need).*?\.\s*",
        r"^(this is|here is)\s+my\s+summary:?\s*",
        r"^\*\*summary\*\*:?\s*",
        r"^summary:?\s*",
        r"^answer:?\s*",
        r"^response:?\s*",
    ]
    
    cleaned = text
    
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    
    # Remove markdown bold/italic
    cleaned = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned)
    cleaned = re.sub(r'\*([^*]+)\*', r'\1', cleaned)
    
    # Remove trailing meta-text
    trailing_patterns = [
        r'\s*i hope this helps!?\s*$',
        r'\s*let me know if .*?$',
        r'\s*please let me know .*?$',
    ]
    
    for pattern in trailing_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()
    
    return cleaned


@router.post("/chat_use_cases/")
def summarize_chat_use_cases(request: SummarizeRequest, request_data: Request):
    """
    Generate a comprehensive summary of chat messages and extracted use cases.
    
    Returns:
    - main_summary: Overall summary of the conversation and requirements
    - use_case_summaries: Individual summaries for each unique use case
    """
    
    user_id = require_user(request_data)
    
    if not request.messages or len(request.messages) == 0:
        raise HTTPException(status_code=400, detail="No messages provided for summarization")
    
    try:
        # Extract all use cases from messages
        all_use_cases = []
        conversation_text = []
        
        for msg in request.messages:
            # Collect conversation content
            if msg.content:
                conversation_text.append(f"{msg.role}: {msg.content}")
            
            # Collect use cases
            if msg.use_cases and len(msg.use_cases) > 0:
                for uc in msg.use_cases:
                    if uc.get("status") == "stored" and uc.get("title"):
                        all_use_cases.append(uc)
        
        if len(all_use_cases) == 0:
            return {
                "main_summary": "No use cases were extracted from this conversation.",
                "use_case_summaries": []
            }
        
        # Generate main summary
        main_summary = generate_main_summary(conversation_text, all_use_cases)
        
        # Generate individual use case summaries
        use_case_summaries = []
        for uc in all_use_cases:
            summary = generate_use_case_summary(uc)
            use_case_summaries.append({
                "title": uc.get("title", "Unknown Use Case"),
                "summary": summary
            })
        
        return {
            "main_summary": main_summary,
            "use_case_summaries": use_case_summaries
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")


@router.get("/session/{session_id}/")
def summarize_session(session_id: str, request_data: Request):
    """
    Generate a summary for an entire session including conversation history and all use cases.
    
    Alternative endpoint that fetches data from the database directly.
    """
    
    user_id = require_user(request_data)
    
    try:
        # Fetch conversation history
        conversation_history = session_db_manager.get_conversation_history(session_id, limit=50)
        
        if not conversation_history or len(conversation_history) == 0:
            raise HTTPException(status_code=404, detail="No conversation history found for this session")
        
        # Fetch all use cases for the session
        use_cases = usecase_db_manager.get_use_case_by_session(session_id)
        
        if not use_cases or len(use_cases) == 0:
            return {
                "main_summary": "No use cases have been extracted in this session yet.",
                "use_case_summaries": []
            }
        
        # Build conversation text
        conversation_text = []
        for msg in conversation_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if content:
                conversation_text.append(f"{role}: {content}")
        
        # Generate main summary
        main_summary = generate_main_summary(conversation_text, use_cases)
        
        # Generate individual use case summaries
        use_case_summaries = []
        for uc in use_cases:
            summary = generate_use_case_summary(uc)
            use_case_summaries.append({
                "title": uc.get("title", "Unknown Use Case"),
                "summary": summary
            })
        
        return {
            "main_summary": main_summary,
            "use_case_summaries": use_case_summaries
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate session summary: {str(e)}")


def generate_main_summary(conversation_text: list, use_cases: list) -> str:
    """
    Generate an overall summary of the conversation and extracted use cases.
    """
    
    # Prepare context - include more conversation for better context
    conversation_snippet = "\n".join(conversation_text[:30])  # Use more messages
    
    # Get use case titles and first main flow step from each
    use_case_details = []
    for uc in use_cases[:10]:  # Limit to first 10 for context
        title = uc.get("title", "Unknown")
        main_flow = uc.get("main_flow", [])
        first_step = main_flow[0] if main_flow else "No steps defined"
        use_case_details.append(f"- {title}: {first_step}")
    
    use_case_context = "\n".join(use_case_details)
    
    # Generate query with direct, no-fluff prompt
    system_instruction = "You are a business analyst. Provide only the summary text with no preamble, commentary, or meta-text."
    
    query_text = f"""Write a 3-5 sentence summary of this requirements session:

Conversation:
{conversation_snippet}

Use Cases ({len(use_cases)} total):
{use_case_context}

Cover: system purpose, key functional areas, primary users, and business value.
Write only the summary. Do not include phrases like "Here's a summary" or "This summary"."""
    
    try:
        # Generate summary with more tokens for detailed response
        outputs = makeQuery(system_instruction, query_text, max_new_tokens=400)
        
        summary = outputs["generated_text"].strip()
        
        # Aggressive cleaning of common LLM fluff
        summary = clean_llm_response(summary)
        
        if len(summary) < 50:
            # Fallback if summary is too short
            return generate_fallback_main_summary(use_cases)
        
        return summary
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Return fallback summary
        return generate_fallback_main_summary(use_cases)


def generate_fallback_main_summary(use_cases: list) -> str:
    """
    Generate a descriptive fallback summary if LLM fails.
    """
    if not use_cases:
        return "This session contains no use cases."
    
    use_case_titles = [uc.get("title", "Unknown") for uc in use_cases]
    
    # Try to identify themes from titles
    themes = set()
    for title in use_case_titles:
        title_lower = title.lower()
        if any(word in title_lower for word in ["login", "authenticate", "sign in", "register"]):
            themes.add("authentication")
        if any(word in title_lower for word in ["search", "find", "browse", "filter"]):
            themes.add("search and discovery")
        if any(word in title_lower for word in ["cart", "checkout", "purchase", "order"]):
            themes.add("e-commerce")
        if any(word in title_lower for word in ["email", "notification", "alert", "message"]):
            themes.add("notifications")
        if any(word in title_lower for word in ["manage", "admin", "configure", "settings"]):
            themes.add("administration")
    
    if themes:
        theme_text = ", ".join(list(themes)[:3])
        return f"This session focuses on {theme_text} functionality with {len(use_cases)} use cases including {', '.join(use_case_titles[:3])}{'...' if len(use_case_titles) > 3 else ''}."
    
    return f"This session extracted {len(use_cases)} use cases: {', '.join(use_case_titles[:3])}{'...' if len(use_case_titles) > 3 else ''}."


def generate_use_case_summary(use_case: dict) -> str:
    """
    Generate a concise, meaningful summary for a single use case using LLM.
    """
    
    title = use_case.get("title", "Unknown Use Case")
    preconditions = use_case.get("preconditions", [])
    main_flow = use_case.get("main_flow", [])
    sub_flows = use_case.get("sub_flows", [])
    alternate_flows = use_case.get("alternate_flows", [])
    outcomes = use_case.get("outcomes", [])
    stakeholders = use_case.get("stakeholders", [])
    
    # Build context for LLM
    preconditions_text = '\n'.join(f'- {p}' for p in preconditions) if preconditions else '- None specified'
    main_flow_text = '\n'.join(f'{i+1}. {step}' for i, step in enumerate(main_flow)) if main_flow else '- None specified'
    sub_flows_text = '\n'.join(f'- {sf}' for sf in sub_flows) if sub_flows else '- None specified'
    alternate_flows_text = '\n'.join(f'- {af}' for af in alternate_flows) if alternate_flows else '- None specified'
    outcomes_text = '\n'.join(f'- {o}' for o in outcomes) if outcomes else '- None specified'
    stakeholders_text = ', '.join(stakeholders) if stakeholders else 'Not specified'
    
    use_case_context = f"""Use Case: {title}

Stakeholders: {stakeholders_text}

Preconditions:
{preconditions_text}

Main Flow:
{main_flow_text}

Sub-flows:
{sub_flows_text}

Alternate Flows:
{alternate_flows_text}

Expected Outcomes:
{outcomes_text}"""
    
    # Generate prompt for LLM with direct instructions
    system_instruction = "You are a requirements analyst. Provide only the summary text with no preamble or commentary."
    
    query_text = f"""{use_case_context}

Write a 2-3 sentence summary explaining the business value, key process, and outcomes.
Write only the summary. Do not include phrases like "Here's a summary" or "This use case"."""
    
    try:
        # Generate summary with LLM
        outputs = makeQuery(system_instruction, query_text, max_new_tokens=200)
        
        summary = outputs["generated_text"].strip()
        
        # Aggressive cleaning
        summary = clean_llm_response(summary)
        
        # Fallback if summary is too short
        if len(summary) < 30:
            summary = generate_fallback_summary(use_case)
        
        return summary
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Return fallback summary on error
        return generate_fallback_summary(use_case)


def generate_fallback_summary(use_case: dict) -> str:
    """
    Generate a simple fallback summary if LLM fails.
    """
    title = use_case.get("title", "Unknown Use Case")
    main_flow = use_case.get("main_flow", [])
    outcomes = use_case.get("outcomes", [])
    
    if main_flow and len(main_flow) > 0:
        first_step = main_flow[0]
        last_step = main_flow[-1] if len(main_flow) > 1 else None
        
        if last_step:
            return f"This use case begins with {first_step.lower()} and concludes with {last_step.lower()}. {outcomes[0] if outcomes else 'The process completes successfully.'}"
        else:
            return f"This use case involves {first_step.lower()}. {outcomes[0] if outcomes else 'The process completes successfully.'}"
    
    return f"This use case handles {title.lower()}."