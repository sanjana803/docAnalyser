from typing import Dict, Any, List
from transformers import pipeline
from ..core.exceptions import LLMServiceError

class LLMService:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.model_name = model_name
        # Initialize the summarization pipeline
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        # Initialize the NER pipeline
        self.ner = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")
        # Initialize the keyword extraction pipeline
        self.keyword_extractor = pipeline("text-classification", model="distilbert-base-uncased")

    def analyze_content(self, content: str, analysis_type: str) -> Dict[str, Any]:
        """
        Analyze content using LLM.
        
        Args:
            content: Text content to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Dict containing analysis results
            
        Raises:
            LLMServiceError: If there's an error with the LLM service
        """
        try:
            results = {}
            
            if analysis_type == "summary":
                # Generate summary
                summary = self.summarizer(content, max_length=130, min_length=30, do_sample=False)
                results["summary"] = summary[0]["summary_text"]
                
            elif analysis_type == "entities":
                # Extract named entities
                entities = self.ner(content)
                results["entities"] = self._process_entities(entities)
                
            elif analysis_type == "keywords":
                # Extract keywords
                keywords = self._extract_keywords(content)
                results["keywords"] = keywords
                
            else:
                # Default to full analysis
                summary = self.summarizer(content, max_length=130, min_length=30, do_sample=False)
                entities = self.ner(content)
                keywords = self._extract_keywords(content)
                
                results = {
                    "summary": summary[0]["summary_text"],
                    "entities": self._process_entities(entities),
                    "keywords": keywords
                }
            
            return {
                "status": "success",
                "analysis_type": analysis_type,
                "results": results
            }
            
        except Exception as e:
            raise LLMServiceError(f"Error analyzing content: {str(e)}")
    
    def _process_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and group entities by type."""
        processed = {}
        for entity in entities:
            entity_type = entity["entity"]
            if entity_type not in processed:
                processed[entity_type] = []
            processed[entity_type].append(entity["word"])
        return processed
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction based on frequency and importance
        words = text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Only consider words longer than 3 characters
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in keywords[:10]]  # Return top 10 keywords 