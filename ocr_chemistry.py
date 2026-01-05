import os
import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np

# 🔹 IMPORTANT: set this to your Tesseract installation path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 🔹 INPUT: folder containing Chemistry PDFs
PDF_DIR = r"C:\Users\Dell\Desktop\Harsh\Projects\classplus chatbot\pdfs\Chemistry"

# 🔹 OUTPUT: folder where Chemistry OCR text files will be saved
OUTPUT_DIR = r"C:\Users\Dell\Desktop\Harsh\Projects\classplus chatbot\ocr_output\Chemistry"

# 🔹 Poppler path (required for pdf2image on Windows)
POPPLER_PATH = r"C:\poppler\Library\bin"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def preprocess_image(pil_image):
    """
    Improves OCR accuracy by:
    - converting to grayscale
    - applying binary threshold
    """
    gray = cv2.cvtColor(np.array(pil_image), cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh


# 🔁 LOOP THROUGH ALL Chemistry PDFs
for filename in os.listdir(PDF_DIR):
    if not filename.lower().endswith(".pdf"):
        continue

    print(f"\n🔍 OCR started for: {filename}")

    pdf_path = os.path.join(PDF_DIR, filename)

    # Convert PDF → list of images (one per page)
    images = convert_from_path(
        pdf_path,
        dpi=300,
        poppler_path=POPPLER_PATH
    )

    chapter_text = ""

    for page_num, img in enumerate(images, start=1):
        processed_img = preprocess_image(img)
        text = pytesseract.image_to_string(processed_img, lang="eng")
        chapter_text += f"\n\n--- Page {page_num} ---\n{text}"

    output_path = os.path.join(
        OUTPUT_DIR,
        filename.replace(".pdf", ".txt")
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(chapter_text)

    print(f"✅ OCR completed → {output_path}")

print("\n🎉 ALL CHEMISTRY PDFs OCR PROCESSED SUCCESSFULLY")
