from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.huggingface import HuggingFaceLLM

class LLMService:
    def __init__(self):
        self.embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.llm = self._initialize_llm()
        self.parser = SimpleNodeParser.from_defaults(
            include_metadata=True,
            chunk_size=1024,
            chunk_overlap=50
        )

    def _initialize_llm(self):
        return HuggingFaceLLM(
            model_name="mistralai/Mistral-7B-Instruct-v0.2",
            tokenizer_name="mistralai/Mistral-7B-Instruct-v0.2",
            context_window=4096,
            max_new_tokens=256,
            device_map="auto",
            model_kwargs={"torch_dtype": "auto"},
            generate_kwargs={
                "temperature": 0.3,
                "top_p": 0.9,
                "repetition_penalty": 1.1
            }
        )

    def build_index(self, nodes):
        return VectorStoreIndex(nodes=nodes, embed_model=self.embed_model)

    def query(self, index, question: str):
        query_engine = index.as_query_engine(
            llm=self.llm,
            response_mode="compact_accumulate",
            similarity_top_k=2,
            include_text=True
        )
        return query_engine.query(question)
