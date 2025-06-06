class DocumentAnalyzerException(Exception):
    """Base exception for document analyzer application."""
    pass

class PDFProcessingError(DocumentAnalyzerException):
    """Raised when there's an error processing PDF files."""
    pass

class LLMServiceError(DocumentAnalyzerException):
    """Raised when there's an error with the LLM service."""
    pass

class FileValidationError(DocumentAnalyzerException):
    """Raised when file validation fails."""
    pass 