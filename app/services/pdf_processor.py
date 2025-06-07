from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict

class PDFProcessor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )

    def load_and_split(self) -> List[Dict]:
        """Load PDF and split into chunks with metadata."""
        # Load PDF
        loader = PyPDFLoader(self.pdf_path)
        pages = loader.load()
        
        # Split pages into chunks
        chunks = []
        for page in pages:
            # Split page content
            page_chunks = self.text_splitter.split_text(page.page_content)
            
            # Add chunks with metadata
            for chunk in page_chunks:
                chunks.append({
                    "page_content": chunk,
                    "metadata": {
                        **page.metadata,
                        "chunk_index": len(chunks)
                    }
                })
        
        return chunks
