import os
import sys
import fitz  # PyMuPDF
from rapidocr_onnxruntime import RapidOCR
import cv2
import numpy as np

# Initialize OCR engine
ocr = RapidOCR()

BANK_DIR = os.path.join(os.path.dirname(__file__), '../exams/bank')
OUTPUT_DIR = os.path.join(BANK_DIR, 'extracted_strategies')

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def preprocess_image(img_bytes):
    """
    Apply image processing to potentially improve OCR results.
    Returns a list of processed images (original, binarized, etc.)
    """
    # Convert bytes to numpy array
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    processed_images = {}
    
    # 1. Original
    processed_images['original'] = img_bytes
    
    # 2. Grayscale + Binary (Otsu's thresholding) - Good for high contrast text
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Encode back to bytes
    _, bin_bytes = cv2.imencode('.png', binary)
    processed_images['binary'] = bin_bytes.tobytes()
    
    return processed_images

def extract_text_via_ocr_multi_strategy(pdf_path, filename_base):
    print(f"Processing: {filename_base}...")
    
    try:
        doc = fitz.open(pdf_path)
        
        # We will store results for each strategy
        results = {
            'original': [],
            'binary': []
        }
        
        for page_num, page in enumerate(doc):
            print(f"  -> Scanning page {page_num + 1}/{len(doc)}...")
            
            # High resolution render
            pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
            img_bytes = pix.tobytes("png")
            
            # Get processed versions
            processed_imgs = preprocess_image(img_bytes)
            
            # Run OCR on each version
            for strategy, p_img_bytes in processed_imgs.items():
                result, elapse = ocr(p_img_bytes)
                page_text = ""
                if result:
                    # Filter low confidence? For now keep all.
                    # result format: [[box, text, score], ...]
                    text_lines = [line[1] for line in result]
                    page_text = "\n".join(text_lines)
                else:
                    page_text = "(No text found)"
                
                results[strategy].append(f"--- P{page_num+1} ({strategy}) ---\n{page_text}")

        # Save all versions
        for strategy, pages in results.items():
            out_path = os.path.join(OUTPUT_DIR, f"{filename_base}_{strategy}.txt")
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write("\n\n".join(pages))
            print(f"    Saved strategy '{strategy}' to: {os.path.basename(out_path)}")
            
        return True
        
    except Exception as e:
        print(f"  -> Error processing {filename_base}: {e}")
        return False

def main():
    print("Starting Multi-Strategy OCR Extraction...")
    
    # List all PDFs
    pdf_files = [f for f in os.listdir(BANK_DIR) if f.lower().endswith('.pdf')]
    
    print(f"Found {len(pdf_files)} PDFs in bank.")
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(BANK_DIR, pdf_file)
        filename_base = os.path.splitext(pdf_file)[0]
        
        # Skip if already processed (check one of the outputs)
        if os.path.exists(os.path.join(OUTPUT_DIR, f"{filename_base}_original.txt")):
            print(f"Skipping {pdf_file} (already processed)")
            continue
            
        extract_text_via_ocr_multi_strategy(pdf_path, filename_base)

if __name__ == "__main__":
    main()
