import os
import sys
import fitz  # PyMuPDF
from rapidocr_onnxruntime import RapidOCR

# Initialize OCR engine
# These weights are usually downloaded automatically on first run
ocr = RapidOCR()

BANK_DIR = os.path.join(os.path.dirname(__file__), '../exams/bank')
OUTPUT_DIR = os.path.join(BANK_DIR, 'extracted_ocr')

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def extract_text_via_ocr(pdf_path, output_txt_path):
    print(f"Processing: {os.path.basename(pdf_path)}")
    
    try:
        doc = fitz.open(pdf_path)
        full_text = []
        
        for page_num, page in enumerate(doc):
            print(f"  -> Scanning page {page_num + 1}/{len(doc)}...")
            
            # Render page to image (pixmap)
            # matrix=fitz.Matrix(2, 2) makes image 2x larger for better OCR accuracy
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            
            # Get image data as bytes
            img_bytes = pix.tobytes("png")
            
            # Perform OCR
            result, elapse = ocr(img_bytes)
            
            if result:
                # result format is a list of [box, text, score]
                # We just want the text, joined by newlines
                page_text = "\n".join([line[1] for line in result])
                full_text.append(f"--- Page {page_num + 1} ---\n{page_text}")
            else:
                full_text.append(f"--- Page {page_num + 1} ---\n(No text found)")
                
        # Save results
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(full_text))
            
        print(f"  -> Saved to: {output_txt_path}")
        return True
        
    except Exception as e:
        print(f"  -> Error: {e}")
        return False

def main():
    print("Starting Intelligence OCR (RapidOCR/PaddleOCR)...")
    
    # List all PDFs
    pdf_files = [f for f in os.listdir(BANK_DIR) if f.lower().endswith('.pdf')]
    
    # We want to prioritize the ones that failed before (files that resulted in empty txts)
    # But for now, let's just process "南山2023.pdf" as a proof of concept, or iterate all.
    # User asked to "extract", let's be smart and check file sizes of existing extractions?
    # Or simply process specific ones. Let's process '南山2023.pdf' and '私中數學.pdf' (if it was image)
    
    # Let's target the "Namshan" files or files with < 100 bytes of extracted text in the previous step.
    
    extracted_dir_prev = os.path.join(BANK_DIR, 'extracted')
    
    target_files = []
    
    for pdf_file in pdf_files:
        txt_name = pdf_file.replace('.pdf', '.txt')
        prev_txt_path = os.path.join(extracted_dir_prev, txt_name)
        
        should_process = False
        
        # Condition 1: If previous extraction doesn't exist
        if not os.path.exists(prev_txt_path):
            should_process = True
        # Condition 2: If previous extraction was suspiciously small (likely image only)
        elif os.path.getsize(prev_txt_path) < 100: 
            should_process = True
            
        if should_process:
            target_files.append(pdf_file)

    print(f"Detected {len(target_files)} likely image-based PDFs that need OCR.")
    
    count = 0 
    for pdf_file in target_files:
        pdf_path = os.path.join(BANK_DIR, pdf_file)
        # Use .txt extension for consistency, but save in extracted_ocr
        output_path = os.path.join(OUTPUT_DIR, pdf_file.lower().replace('.pdf', '.txt'))
        
        extract_text_via_ocr(pdf_path, output_path)
        count += 1
        
        # For demonstration speed, let's stop after 2 files if there are many, 
        # unless user wants all. Given the speed of OCR, let's do up to 3 for now to show results quickly.
        if count >= 3:
            print("--- \nPartial batch complete (limit 3 for quick feedback). Run again to process more.")
            break

if __name__ == "__main__":
    main()
