# DocAnalyser

DocAnalyser is a FastAPI-based service for analyzing PDF documents using advanced NLP and LLM techniques. It provides powerful document analysis capabilities including text extraction, summarization, entity recognition, and keyword extraction.

## Features
- PDF text extraction and processing
- Document summarization using BART model
- Named Entity Recognition (NER) using BERT
- Keyword extraction and analysis
- RESTful API endpoints for easy integration
- Caching support with Redis
- Docker support for containerized deployment

## Setup

1. **Clone the repository**
2. **Set up the environment:**
   ```bash
   bash setup.sh
   ```
   This will:
   - Create a Python virtual environment
   - Install all required dependencies
   - Check for Redis installation
   - Create necessary directories

3. **Start Redis (optional, for caching):**
   ```bash
   redis-server
   ```

4. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Usage

The service provides the following endpoints:

### 1. Document Analysis
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "example.pdf",
    "analysis_type": "summary",
    "options": {
      "highlight_keywords": true,
      "extract_entities": true,
      "generate_summary": true
    }
  }'
```

Available analysis types:
- `summary`: Generate document summary
- `entities`: Extract named entities
- `keywords`: Extract key terms
- Default: Full analysis (summary + entities + keywords)

### 2. Root Endpoint
```bash
curl http://localhost:8000/
```

## Docker Support

Build and run using Docker:
```bash
docker build -t docanalyser .
docker run -p 8000:8000 docanalyser
```

## Project Structure
```
document-analyzer/
├── app/
│   ├── core/           # Core models and exceptions
│   ├── services/       # PDF and LLM services
│   ├── utils/          # Utility functions
│   ├── routes/         # API endpoints
│   └── main.py         # Application entry point
├── requirements.txt    # Python dependencies
└── Dockerfile         # Docker configuration
```

## Dependencies
- Python 3.9+
- FastAPI
- Uvicorn
- PyMuPDF
- Transformers
- Sentence-Transformers
- Redis (optional, for caching)
- Docker (optional, for containerization)

## License
MIT License 