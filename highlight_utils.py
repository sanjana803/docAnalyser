import fitz  # PyMuPDF
from PIL import Image, ImageDraw
import os
import re

def find_phrase_bbox(page, phrase):
    words = page.get_text("words") 
    phrase = phrase.strip().replace("\n", " ")
    phrase_words = re.findall(r"\w+", phrase)
    word_texts = [w[4] for w in words]
    # Find the start index where the phrase matches
    for i in range(len(word_texts)):
        for j in range(i+1, len(word_texts)+1):
            candidate = ' '.join(word_texts[i:j])
            candidate_norm = re.sub(r'\W+', '', candidate).lower()
            phrase_norm = re.sub(r'\W+', '', ' '.join(phrase_words)).lower()
            if candidate_norm == phrase_norm:
                word_bboxes = [words[k][:4] for k in range(i, j)]
                x0 = min(w[0] for w in word_bboxes)
                y0 = min(w[1] for w in word_bboxes)
                x1 = max(w[2] for w in word_bboxes)
                y1 = max(w[3] for w in word_bboxes)
                return [x0, y0, x1, y1]
    return None

def highlight_answers(doc_path, answers, output_dir="output_images"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    doc = fitz.open(doc_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        draw = ImageDraw.Draw(img)
        found = False
        for answer in answers:
            clean_answer = answer.strip()
            if clean_answer.lower().startswith('response'):
                continue
            bbox = find_phrase_bbox(page, clean_answer)
            if bbox:
                x0, y0, x1, y1 = bbox
                pdf_width, pdf_height = page.rect.width, page.rect.height
                x0_img = x0
                x1_img = x1
                y0_img = pdf_height - y1
                y1_img = pdf_height - y0
                draw.rectangle(
                    [x0_img, y0_img, x1_img, y1_img],
                    outline="red",
                    width=3,
                )
                found = True
        if found:
            output_path = os.path.join(output_dir, f"highlight_page_{page_num+1}.png")
            img.save(output_path)
    doc.close()

def extract_organization(answer):
    # Remove lines like 'Response 1:' and empty lines
    lines = [l.strip() for l in answer.split('\n') if l.strip() and not l.strip().lower().startswith('response')]
    # Regex for org/institute/college/school/university
    matches = []
    for l in lines:
        found = re.findall(r'([A-Z][A-Za-z&.,()\\- ]*(institute|university|college|school)[A-Za-z&.,()\\- ]*)', l, re.IGNORECASE)
        if found:
            matches.extend([m[0].strip() for m in found])
    # Only return matches, do not fallback to all lines
    return matches
