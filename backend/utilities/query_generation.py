import json
from typing import Dict

"""
query_manager.py
Consolidates all query prompt generation to a single location, allowing for easy debugging
"""

REFINE_INSTRUCTIONS = {
    "more_main_flows": "Add more main flows (additional primary flows or steps) to this use case. Expand the main flow with more detailed or additional steps.",
    "more_sub_flows": "Add more sub flows to this use case. Include additional branching scenarios, related flows, or secondary paths.",
    "more_alternate_flows": "Add more alternate flows to this use case. Include alternative paths, edge cases, error scenarios, and exception handling flows.",
    "more_preconditions": "Add more preconditions to this use case. Include additional requirements, system states, or conditions that must be met before the use case can execute.",
    "more_stakeholders": "Add more stakeholders to this use case. Identify additional actors, users, systems, or entities involved in this use case."
}

DEFAULT_REFINE_INSTRUCTION = "Improve the overall quality and completeness of this use case."

def refineQueryGeneration(use_case: Dict, refinement_type: str) -> str:

    """
    Returns a query to refine the current use case
    """
    instruction = REFINE_INSTRUCTIONS.get(refinement_type)
    
    if instruction is None:
        instruction = DEFAULT_REFINE_INSTRUCTION

    queryText = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
                    You are a requirements analyst refining a use case.
                    <|eot_id|><|start_header_id|>user<|end_header_id|>
                    Current use case:
                    {json.dumps(use_case, indent=2)}
                    Task: {instruction}
                    Return the refined use case in the same JSON format, with improvements applied.
                    <|eot_id|><|start_header_id|>assistant<|end_header_id|>
                """
    
    return queryText

def requirementsQueryGeneration(context: str, question: str):

    """
    Generate a query regarding questions about the requirements
    """

    query = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
                You are a requirements analyst assistant. Answer questions about use cases clearly and concisely.
                IMPORTANT: Do NOT mention use case IDs, numbers, or database identifiers in your responses. Only refer to use cases by their titles.
                <|eot_id|><|start_header_id|>user<|end_header_id|>
                Use cases:
                {context}
                Question: {question}
                Provide a clear, helpful answer based on the use cases above. Do not include any use case numbers or IDs in your response.
                <|eot_id|><|start_header_id|>assistant<|end_header_id|>
                """
    
    return query


########################################
#             RAG Queries              #
########################################

def summarize_session_queryGen(conversationText: str) -> str:
    """
    Generates a query for Summarizing a Session
    
    :param conversationText: The Combined text from a conversation
    :type conversationText: str
    :return: The Generated Query for an LLM
    :rtype: str
    """

    query = f"""Summarize the following conversation about software requirements in 2-3 sentences:
                {conversationText}
                Summary:"""
    
    return query

########################################
#       Session_Manager Queries        #
########################################

def session_title_queryGen(text: str) -> str:
    """
    Generates a query for getting a sesson title
    
    :param text: The requirments text to be summarized
    :type text: str
    :return: The Generated Query for an LLM
    :rtype: str
    """

    query = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
            You are a requirements analyst. Create a concise session title (4-7 words) that summarizes this requirement text.
            <|eot_id|><|start_header_id|>user<|end_header_id|>
            Requirements text:
            {text}
            Generate a short, descriptive title (4-7 words):
            <|eot_id|><|start_header_id|>assistant<|end_header_id|>
            """
    
    return query

########################################
#       Use_Case_Manager Queries       #
########################################

def uc_single_stage_extract_queryGen(max_use_cases: id, memory_context: str, text:str) -> str:
    query = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
                You are a requirements analyst. Extract use cases from text and return them as JSON.
                CRITICAL RULES:
                1. Each action mentioned should be a SEPARATE use case
                2. DO NOT create duplicate use cases with the same title
                3. Each use case must be unique and distinct
                4. Split compound actions: "logs in and adds" → 2 separate use cases
                <|eot_id|><|start_header_id|>user<|end_header_id|>
                {memory_context}
                Requirements:
                {text}
                Extract approximately {max_use_cases} UNIQUE, DISTINCT use cases from the requirements above.
                IMPORTANT: 
                - "User logs in and adds to cart" → Create 2 separate use cases:
                1. "User logs in to system"  
                2. "User adds items to cart"
                - DO NOT create the same use case twice
                - Each use case must have a different title
                Return a JSON array where EACH use case has UNIQUE title and purpose:
                [
                {{
                    "title": "User logs in to system",
                    "preconditions": ["User has valid credentials"],
                    "main_flow": ["User opens app", "User enters credentials", "System validates", "User is authenticated"],
                    "sub_flows": ["User can reset password", "User can remember device"],
                    "alternate_flows": ["If invalid: System shows error", "If locked: System requires unlock"],
                    "outcomes": ["User is logged in successfully"],
                    "stakeholders": ["User", "Authentication System"]
                }},
                {{
                    "title": "User adds items to shopping cart",
                    "preconditions": ["User is logged in", "Products are available"],
                    "main_flow": ["User browses products", "User selects product", "User clicks add to cart", "System adds item", "Cart is updated"],
                    "sub_flows": ["User can adjust quantity", "User can view cart"],
                    "alternate_flows": ["If out of stock: System notifies user", "If cart full: System prompts checkout"],
                    "outcomes": ["Item added to cart successfully"],
                    "stakeholders": ["User", "Shopping Cart System", "Inventory System"]
                }}
                ]
                <|eot_id|><|start_header_id|>assistant<|end_header_id|>
                ["""
    return query

def uc_batch_extract_queryGen(batch_count: id, memory_context: str, text:str) -> str:

    """
    Generate a query for the Single Stage Use Cases Extraction
    """

    query = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
            You are a requirements analyst. Extract exactly {batch_count} use cases from the requirements.
            <|eot_id|><|start_header_id|>user<|end_header_id|>
            {memory_context}
            Requirements:
            {text}
            Extract exactly {batch_count} distinct use cases. Return ONLY a JSON array:
            [
            {{
                "title": "Actor performs action on object",
                "preconditions": ["Precondition 1", "Precondition 2"],
                "main_flow": ["Step 1", "Step 2", "Step 3", "Step 4"],
                "sub_flows": ["Optional feature 1", "Optional feature 2"],
                "alternate_flows": ["Error case 1", "Error case 2"],
                "outcomes": ["Success result 1", "Success result 2"],
                "stakeholders": ["Actor", "System"]
            }}
            ]
            <|eot_id|><|start_header_id|>assistant<|end_header_id|>
            ["""
    
    return query