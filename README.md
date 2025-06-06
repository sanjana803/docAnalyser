# DocAnalyser

DocAnalyser is a Python-based tool for analyzing PDF documents and visually highlighting answers to user queries, such as extracting organization or institute names from resumes or reports.

## Features
- Extracts relevant information (e.g., organization names) from PDF documents using LLMs and regex.
- Highlights the extracted answers directly on the PDF pages and saves them as images.
- Supports custom queries and answer extraction logic.

## Setup

1. **Clone the repository**
2. **Set up a Python virtual environment:**
   ```bash
   bash setup.sh
   ```
3. **Add your PDF file:**
   Place your PDF (e.g., `example.pdf`) in the project directory.
4. **Configure environment variables:**
   - Create a `.env` file with your OpenAI API key or other required keys.

## Usage

1. **Run the main script:**
   ```bash
   python main.py
   ```
2. **What happens:**
   - The script loads the PDF, extracts text, and uses an LLM to answer a query (e.g., "Extract and name any educational institute or organization mentioned in the document.").
   - The answer is parsed to extract organization names.
   - The script highlights these names in the PDF and saves annotated images in the `output_images` directory.

## Customization
- You can modify the query or the extraction logic in `main.py` and `highlight_utils.py` to suit your needs.

## Dependencies
- Python 3.8+
- PyMuPDF
- Pillow
- llama-index
- sentence-transformers
- transformers
- torch
- python-dotenv

Install dependencies using the provided `setup.sh` script.

## License
MIT License 