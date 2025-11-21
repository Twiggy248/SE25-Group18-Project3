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