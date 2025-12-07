import json
from typing import Dict

"""
query_manager.py
Consolidates all query prompt generation to a single location, allowing for easy debugging
"""

SYSTEM_ROLE_CONTEXT = "You are a requirements analyst"

def refineQueryGeneration(use_case: Dict, refinement_type: str) -> list[str]:

    """
    Returns a query to refine the current use case
    """

    REFINE_INSTRUCTIONS = {
        "more_main_flows": "Add more main flows (additional primary flows or steps) to this use case. Expand the main flow with more detailed or additional steps.",
        "more_sub_flows": "Add more sub flows to this use case. Include additional branching scenarios, related flows, or secondary paths.",
        "more_alternate_flows": "Add more alternate flows to this use case. Include alternative paths, edge cases, error scenarios, and exception handling flows.",
        "more_preconditions": "Add more preconditions to this use case. Include additional requirements, system states, or conditions that must be met before the use case can execute.",
        "more_stakeholders": "Add more stakeholders to this use case. Identify additional actors, users, systems, or entities involved in this use case."
    }

    DEFAULT_REFINE_INSTRUCTION = "Improve the overall quality and completeness of this use case."



    instruction = REFINE_INSTRUCTIONS.get(refinement_type)
    
    if instruction is None:
        instruction = DEFAULT_REFINE_INSTRUCTION


    systemInstruction = f"{SYSTEM_ROLE_CONTEXT} refining use cases. Always respond using JSON."

    queryText = f"""Current use case:
                    {json.dumps(use_case, indent=2)}
                    Task: {instruction}"""
    
    return [systemInstruction, queryText]

def requirementsQueryGeneration(context: str, question: str) -> list[str]:

    """
    Generate a query regarding questions about the requirements
    """

    systemInstruction = f"{SYSTEM_ROLE_CONTEXT} providing clear and concise answers to questions. Only use the titles of use cases, and never return system ids."

    queryText = f"""Use cases:
                    {context}
                    Question: {question}
                    """
    
    return [systemInstruction, queryText]


########################################
#             RAG Queries              #
########################################

def summarize_session_queryGen(conversationText: str) -> list[str]:
    """
    Generates a query for Summarizing a Session
    
    :param conversationText: The Combined text from a conversation
    :type conversationText: str
    :return: The Generated Query for an LLM
    :rtype: str
    """

    systemInstruction = f"{SYSTEM_ROLE_CONTEXT} summarizing conversations regarding requirements and use cases being clear and concise, and using a maximum of 3 sentences."

    queryText = f"Summarize the following conversation:{conversationText}"
    
    return [systemInstruction, queryText]

########################################
#       Session_Manager Queries        #
########################################

def session_title_queryGen(text: str) -> list[str]:
    """
    Generates a query for getting a sesson title
    
    :param text: The requirments text to be summarized
    :type text: str
    :return: The Generated Query for an LLM
    :rtype: str
    """
    systemInstruction = f"{SYSTEM_ROLE_CONTEXT} creating titles of 4-7 words based on provided text."
    
    queryText = f"Provide a title based on the following Requirements Text: {text}"
    
    return [systemInstruction, queryText]

########################################
#       Use_Case_Manager Queries       #
########################################

def uc_single_stage_extract_queryGen(max_use_cases: id, memory_context: str, text:str) -> list[str]:

    systemInstruction = f"""{SYSTEM_ROLE_CONTEXT} extracting use cases from provided text and returning as JSON. CRITICAL RULES:
                            1. Each action mentioned should be a SEPARATE use case, and compound actions must be split into separate use cases
                            2. Each use case must be unique, distinct, and have a unique title
                            """

    queryText = f"""{memory_context}
                    
                    Extract approximately {max_use_cases} UNIQUE, DISTINCT use cases from the requirements text below.
                    Return a JSON array where EACH use case has UNIQUE title and purpose:
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
                    
                    Requirements:
                    {text}"""
    
    return [systemInstruction, queryText]

def uc_batch_extract_queryGen(batch_count: id, memory_context: str, text:str) -> list[str]:

    """
    Generate a query for the Single Stage Use Cases Extraction
    """

    systemInstruction = f"""{SYSTEM_ROLE_CONTEXT} extracting use cases from provided text and returning as JSON. CRITICAL RULES:
                            1. Each action mentioned should be a SEPARATE use case, and compound actions must be split into separate use cases
                            2. Each use case must be unique, distinct, and have a unique title
                            """

    queryText = f"""{memory_context}
                    
                    Extract exactly {batch_count} UNIQUE, DISTINCT use cases from the requirements text below.
                    Return a JSON array where EACH use case has UNIQUE title and purpose:
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
                    
                    Requirements:
                    {text}"""
    
    return [systemInstruction, queryText]