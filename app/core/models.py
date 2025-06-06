from pydantic import BaseModel, Field
from typing import Optional, List

class AnalysisRequest(BaseModel):
    pdf_path: str = Field(..., description="Path to PDF document")
    query: str = Field(..., description="Natural language query")
    output_dir: Optional[str] = Field("output_images", description="Output directory for highlights")

class AnalysisResponse(BaseModel):
    answer: List[str]
    visualization_paths: List[str]
    processing_time: float
    confidence: Optional[float]
    error: Optional[str]

class DocumentAnalysisRequest(BaseModel):
    file_path: str
    analysis_type: str
    options: Optional[dict] = None

class DocumentAnalysisResponse(BaseModel):
    status: str
    results: dict
    highlights: Optional[List[dict]] = None
    error: Optional[str] = None
