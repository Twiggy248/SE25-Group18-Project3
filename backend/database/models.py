"""
Models.py
Contains the Schemas for the Database Models utilized in the backend
"""


from pydantic import BaseModel
from typing import List, Optional

class UseCaseSchema(BaseModel):
    title: str
    preconditions: List[str]
    main_flow: List[str]
    sub_flows: List[str]
    alternate_flows: List[str]
    outcomes: List[str]
    stakeholders: List[str]


class InputText(BaseModel):
    raw_text: str
    session_id: Optional[str] = None
    project_context: Optional[str] = None
    domain: Optional[str] = None


class SessionRequest(BaseModel):
    session_id: Optional[str] = None
    project_context: Optional[str] = None
    domain: Optional[str] = None


class RefinementRequest(BaseModel):
    use_case_id: int
    refinement_type: str
    custom_instruction: Optional[str] = None


class QueryRequest(BaseModel):
    session_id: str
    question: str
