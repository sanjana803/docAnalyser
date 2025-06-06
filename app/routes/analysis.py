from fastapi import APIRouter, HTTPException
from ..core.models import DocumentAnalysisRequest, DocumentAnalysisResponse
from ..services.pdf_processor import PDFProcessor
from ..services.llm_service import LLMService
from ..utils.file_utils import validate_file_path

router = APIRouter()
pdf_processor = PDFProcessor()
llm_service = LLMService()

@router.post("/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document(request: DocumentAnalysisRequest):
    """
    Analyze a document and return results.
    
    Args:
        request: DocumentAnalysisRequest object containing file path and analysis type
        
    Returns:
        DocumentAnalysisResponse object containing analysis results
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        # Validate file
        validate_file_path(request.file_path)
        
        # Process PDF
        pdf_content = pdf_processor.process_document(request.file_path)
        
        # Analyze content
        analysis_results = llm_service.analyze_content(
            pdf_content["content"],
            request.analysis_type
        )
        
        return DocumentAnalysisResponse(
            status="success",
            results=analysis_results,
            highlights=analysis_results.get("highlights")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
