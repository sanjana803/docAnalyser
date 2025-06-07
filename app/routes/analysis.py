from fastapi import APIRouter, HTTPException
from app.core.models import AnalysisRequest, AnalysisResponse, AnswerItem
from app.services.pdf_processor import PDFProcessor
from app.services.llm_service import LLMService
import os

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
def analyze_document(request: AnalysisRequest):
    if not os.path.exists(request.pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found")
    os.makedirs(request.reference_path, exist_ok=True)

    pdf_processor = PDFProcessor(request.pdf_path)
    documents = pdf_processor.load_and_split()

    llm_service = LLMService()  # No parameters needed
    results = llm_service.analyze(documents, request.questions, request.reference_path)
    return AnalysisResponse(results=[AnswerItem(**item) for item in results])
