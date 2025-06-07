from typing import List, Dict
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch
from tqdm import tqdm

class LLMService:
    def __init__(self):
        # Initialize the embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize the QA model
        self.qa_model = AutoModelForQuestionAnswering.from_pretrained('deepset/roberta-base-squad2')
        self.qa_tokenizer = AutoTokenizer.from_pretrained('deepset/roberta-base-squad2')
        
        # Initialize FAISS index
        self.dimension = 384  # Dimension of the embeddings
        self.index = faiss.IndexFlatL2(self.dimension)
        self.text_chunks = []
        self.metadata = []

    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for the given texts."""
        embeddings = []
        for text in tqdm(texts, desc="Creating embeddings"):
            embedding = self.embedding_model.encode(text)
            embeddings.append(embedding)
        return np.array(embeddings)

    def build_vectorstore(self, documents: List[Dict], reference_path: str = None):
        """Build the vector store from documents."""
        # Extract text chunks and metadata
        self.text_chunks = [doc["page_content"] for doc in documents]
        self.metadata = [doc["metadata"] for doc in documents]
        
        # Create embeddings
        embeddings = self.create_embeddings(self.text_chunks)
        
        # Add to FAISS index
        self.index.add(embeddings)

    def _prepare_context(self, question: str, top_k: int = 5) -> str:
        """Prepare context for QA by retrieving relevant chunks."""
        # Get question embedding
        question_embedding = self.embedding_model.encode([question])[0]
        
        # Search for similar chunks
        distances, indices = self.index.search(np.array([question_embedding]), top_k)
        
        # Combine chunks with metadata
        context_parts = []
        for idx in indices[0]:
            if idx < len(self.text_chunks):
                chunk = self.text_chunks[idx]
                meta = self.metadata[idx]
                context_parts.append(f"[Page {meta.get('page', 'N/A')}] {chunk}")
        
        return "\n\n".join(context_parts)

    def _format_answer(self, answer: str, confidence: float, sources: List[Dict]) -> Dict:
        """Format the answer with source information."""
        # Remove duplicate sources
        unique_sources = []
        seen_pages = set()
        for source in sources:
            page = source.get("page", "N/A")
            if page not in seen_pages:
                seen_pages.add(page)
                unique_sources.append(source)
        
        return {
            "answer": answer,
            "confidence": confidence,
            "sources": unique_sources
        }

    def analyze(self, documents: List[Dict], questions: List[str], reference_path: str = None) -> List[Dict]:
        """Analyze the documents and answer the questions."""
        # Build vector store if not already built
        if not self.text_chunks:
            self.build_vectorstore(documents, reference_path)
        
        results = []
        for question in questions:
            # Prepare context
            context = self._prepare_context(question)
            
            # Prepare inputs for QA model
            inputs = self.qa_tokenizer(
                question,
                context,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            )
            
            # Get model predictions
            with torch.no_grad():
                outputs = self.qa_model(**inputs)
            
            # Get answer span
            answer_start = torch.argmax(outputs.start_logits)
            answer_end = torch.argmax(outputs.end_logits)
            
            # Ensure valid answer span
            if answer_end < answer_start:
                answer_end = answer_start
            
            # Get answer text and clean it
            answer_tokens = inputs["input_ids"][0][answer_start:answer_end+1]
            answer = self.qa_tokenizer.decode(answer_tokens, skip_special_tokens=True)
            
            # If answer is empty or just special tokens, try to get a better answer
            if not answer.strip() or answer.strip() in ["<s>", "</s>", "[CLS]", "[SEP]"]:
                # Get top 3 possible answers
                start_scores = torch.softmax(outputs.start_logits, dim=1)[0]
                end_scores = torch.softmax(outputs.end_logits, dim=1)[0]
                
                # Get top start and end positions
                top_start = torch.topk(start_scores, k=3)
                top_end = torch.topk(end_scores, k=3)
                
                # Try different combinations
                best_answer = ""
                best_score = 0
                
                for start_idx in top_start.indices:
                    for end_idx in top_end.indices:
                        if end_idx >= start_idx:
                            score = start_scores[start_idx].item() + end_scores[end_idx].item()
                            if score > best_score:
                                answer_tokens = inputs["input_ids"][0][start_idx:end_idx+1]
                                candidate = self.qa_tokenizer.decode(answer_tokens, skip_special_tokens=True)
                                if candidate.strip() and candidate.strip() not in ["<s>", "</s>", "[CLS]", "[SEP]"]:
                                    best_answer = candidate
                                    best_score = score
                
                answer = best_answer if best_answer else "I couldn't find a specific answer to this question in the document."
            
            # Calculate confidence
            start_confidence = torch.softmax(outputs.start_logits, dim=1)[0][answer_start].item()
            end_confidence = torch.softmax(outputs.end_logits, dim=1)[0][answer_end].item()
            confidence = (start_confidence + end_confidence) / 2
            
            # Get sources
            sources = []
            for idx in range(len(self.text_chunks)):
                if self.text_chunks[idx] in context:
                    sources.append(self.metadata[idx])
            
            # Format and add result
            result = self._format_answer(answer, confidence, sources)
            result["question"] = question
            results.append(result)
        
        return results
