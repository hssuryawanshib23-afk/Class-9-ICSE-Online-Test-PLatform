import os
import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np

# 🔹 IMPORTANT: set this to your Tesseract installation path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 🔹 INPUT: Biology PDFs folder
PDF_DIR = r"C:\Users\Dell\Desktop\Harsh\Projects\classplus chatbot\pdfs\Biology"

# 🔹 OUTPUT: Biology OCR output folder
OUTPUT_DIR = r"C:\Users\Dell\Desktop\Harsh\Projects\classplus chatbot\ocr_output\Biology"

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


def clean_filename(filename):
    """Convert PDF filename to clean output name"""
    name = filename.replace(".pdf", "")
    # Standardize naming: biology-selina-chapter-X-title.txt
    if "chapter-" in name.lower():
        # Already has chapter format
        return f"biology-selina-{name}.txt"
    elif name.startswith("Chapter "):
        # Simple "Chapter 1.pdf" format
        chapter_num = name.split()[1]
        return f"biology-selina-chapter-{chapter_num}.txt"
    else:
        return f"biology-selina-{name}.txt"


# 🔁 LOOP THROUGH ALL Biology PDFs
print("🧬 Starting Biology OCR Processing...")
print(f"📁 Input: {PDF_DIR}")
print(f"📁 Output: {OUTPUT_DIR}\n")

pdf_files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]
total_files = len(pdf_files)

for idx, filename in enumerate(pdf_files, 1):
    print(f"[{idx}/{total_files}] 🔍 OCR started for: {filename}")

    pdf_path = os.path.join(PDF_DIR, filename)

    try:
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
            
            # Progress indicator for long PDFs
            if page_num % 5 == 0:
                print(f"    📄 Processed {page_num}/{len(images)} pages...")

        output_filename = clean_filename(filename)
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(chapter_text)

        print(f"✅ OCR completed → {output_filename}\n")

    except Exception as e:
        print(f"❌ Error processing {filename}: {str(e)}\n")
        continue

print("🎉 ALL BIOLOGY PDFs OCR PROCESSED SUCCESSFULLY")
print(f"📊 Total files processed: {total_files}")
print(f"📁 Output location: {OUTPUT_DIR}")
