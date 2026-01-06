import os
import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np

# Set Tesseract path (change if installed elsewhere)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Folders
PDF_DIR = r"pdfs"
OUTPUT_DIR = r"output"
POPPLER_PATH = r"C:\poppler\Library\bin"

# Create output folder if doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def preprocess_image(pil_image):
    """Improve image quality for better OCR"""
    gray = cv2.cvtColor(np.array(pil_image), cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh

# Process all PDFs
for filename in os.listdir(PDF_DIR):
    if not filename.lower().endswith(".pdf"):
        continue
    
    print(f"Processing: {filename}")
    pdf_path = os.path.join(PDF_DIR, filename)
    
    # Convert PDF to images (one per page)
    images = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
    
    chapter_text = ""
    for page_num, img in enumerate(images, start=1):
        processed_img = preprocess_image(img)
        text = pytesseract.image_to_string(processed_img, lang="eng")
        chapter_text += f"\n--- Page {page_num} ---\n{text}"
    
    # Save to text file
    output_path = os.path.join(OUTPUT_DIR, filename.replace(".pdf", ".txt"))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(chapter_text)
    
    print(f"✓ Completed: {output_path}")

print("\n🎉 ALL PDFs PROCESSED!")