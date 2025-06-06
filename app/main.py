from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.analysis import router as analysis_router
from app.core import exceptions

app = FastAPI(
    title="Document Analyzer API",
    description="API for analyzing documents using LLM",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to Document Analyzer API"}

# Exception handlers
@app.exception_handler(exceptions.DocumentProcessingError)
async def document_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)}
    )
