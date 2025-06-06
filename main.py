import os
import time
from dotenv import load_dotenv
import re
from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.readers.file import PDFReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core.schema import Document
from highlight_utils import highlight_answers

# Load API key and env
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Initialize embedding and local LLM
# Embedding model
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Local LLM
llm = HuggingFaceLLM(
    model_name="facebook/opt-350m",
    tokenizer_name="facebook/opt-350m",
    context_window=1024,
    max_new_tokens=64,
    device_map="auto",
    model_kwargs={
        "torch_dtype": "auto",
        "low_cpu_mem_usage": True
    },
    generate_kwargs={
        "temperature": 0.3,
        "do_sample": True,
        "top_p": 0.9,
        "repetition_penalty": 1.1
    }
)

# Load PDF and parse using PyMuPDF to get bboxes
pdf_path = "example.pdf"

import fitz # PyMuPDF

def get_union_bbox(word_bboxes):
    if not word_bboxes:
        return None
    x0 = min(w[0] for w in word_bboxes)
    y0 = min(w[1] for w in word_bboxes)
    x1 = max(w[2] for w in word_bboxes)
    y1 = max(w[3] for w in word_bboxes)
    return [x0, y0, x1, y1]

doc = fitz.open(pdf_path)
nodes = []
for page_num in range(len(doc)):
    page = doc.load_page(page_num)
    words = page.get_text("words")  # list of (x0, y0, x1, y1, word, block_no, line_no, word_no)
    page_text = page.get_text()
    # We'll split the page text into lines and try to match lines to words
    lines = page_text.splitlines()
    word_idx = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Find the sequence of words that matches this line
        line_words = []
        line_text = ''
        while word_idx < len(words) and len(line_text) < len(line):
            word = words[word_idx]
            word_str = word[4]
            if line_text:
                line_text += ' '
            line_text += word_str
            line_words.append(word)
            word_idx += 1
        # If the line_text matches the line, use the union bbox
        if line_text.replace(' ', '') == line.replace(' ', ''):
            word_bboxes = [w[:4] for w in line_words]
            union_bbox = get_union_bbox(word_bboxes)
        else:
            union_bbox = None
        doc_chunk = Document(
            text=line,
            metadata={
                "page_label": str(page_num + 1),
                "file_name": os.path.basename(pdf_path),
                "bbox": union_bbox
            }
        )
        nodes.append(doc_chunk)
doc.close()

# Parse documents to nodes with metadata (SimpleNodeParser for splitting)
parser = SimpleNodeParser.from_defaults(
    include_metadata=True,
    include_prev_next_rel=True,
    chunk_size=1024,  # Increase chunk size for fewer nodes
    chunk_overlap=50
)
nodes = parser.get_nodes_from_documents(nodes) # Pass the created document chunks here

# Build index
index = VectorStoreIndex(nodes=nodes, embed_model=embed_model)

# Query engine with source nodes
query_engine = index.as_query_engine(
    llm=llm,
    response_mode="compact_accumulate",
    similarity_top_k=2,
    include_text=True
)

# Ask question
question = "Extract and name any educational institute or organization mentioned in the document."
start = time.time()
response = query_engine.query(question)
end = time.time()

# Output
print("\n📌 Answer:", response.response)
print("⏱ Took:", int((end - start) * 1000), "ms")

# Debug context
print("\n📄 Context nodes used:")
for node in response.source_nodes:
    # Print the bbox metadata of the source node
    bbox_meta = node.metadata.get('bbox', 'N/A')
    page_meta = node.metadata.get('page_label', 'N/A')
    print(f"→ Page {page_meta}, Bbox: {bbox_meta}")
    print(node.node.get_content().strip()[:200] + '...')

def extract_organization(answer):
    # Try to extract a phrase that looks like an institute/organization name
    # This regex matches lines with 'institute', 'university', 'college', or 'school' (case-insensitive)
    matches = re.findall(r'([A-Z][A-Za-z&.,()\- ]*(institute|university|college|school)[A-Za-z&.,()\- ]*)', answer, re.IGNORECASE)
    if matches:
        # Return only the matched phrase(s), strip whitespace
        return [m[0].strip() for m in matches]
    # fallback: return the first line or the answer itself
    return [answer.split('\n')[0].strip()]

# After getting response.response
answers = extract_organization(response.response)
highlight_answers(pdf_path, answers)
