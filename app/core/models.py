from pydantic import BaseModel
from typing import List, Dict, Any

class AnalysisRequest(BaseModel):
    pdf_path: str
    reference_path: str
    questions: List[str]

class AnswerItem(BaseModel):
    question: str
    answer: str
    sources: List[Dict[str, Any]]

class AnalysisResponse(BaseModel):
    results: List[AnswerItem]
