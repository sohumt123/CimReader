import fitz
import os
from pathlib import Path

MIN_AREA_RATIO = 0.05   # must cover ≥5% of page area
MIN_PX_WIDTH   = 100    # at least 200 px wide
MIN_PX_HEIGHT  = 100    # at least 200 px tall

# Get the root directory
ROOT_DIR = Path(__file__).parent.parent

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text_blocks = []
    for page_number in range(len(doc)):
        page = doc[page_number]
        text = page.get_text("text")
        if text.strip():
            text_blocks.append((page_number, text))
    return text_blocks

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python extract_text.py <path_to_pdf>")
        sys.exit(1)
    pdf_path = sys.argv[1]
    blocks = extract_text_from_pdf(pdf_path)

    with open(ROOT_DIR / "text.text", "w", encoding="utf-8") as f:
        for page_num, text in blocks:
            f.write(f"--- Page {page_num + 1} ---\n")
            f.write(text[:1000000] + "\n\n")  # show  the text
