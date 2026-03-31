import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import time
import sys
import os
import re
from deep_translator import GoogleTranslator

# Configuration
PDF_FILE_PATH = "PDF_NAME.PDF"
START_PAGE = 1  # User indicated the Sanskrit text starts at page 17 (1-indexed page 17 means index 16)
OUTPUT_FILE = "Sanskrit_Translation_Output.txt"

# Setting OCR Language: 'san' is Sanskrit
# Make sure `tesseract-ocr` and `tesseract-ocr-san` are installed!
OCR_LANG = 'san' 

def process_and_translate_page(page, translator):
    """
    Extracts the image of the page, runs OCR, and translates it.
    Returns the original OCR text and the translated text.
    """
    # 1. Convert PDF page to an image.
    # We use a matrix to zoom in for better OCR resolution (DPI ~300)
    zoom_x = 2.0  
    zoom_y = 2.0  
    mat = fitz.Matrix(zoom_x, zoom_y)
    pix = page.get_pixmap(matrix=mat)

    # 2. Load into PIL
    img_data = pix.tobytes("png")
    img = Image.open(io.BytesIO(img_data))

    # 3. Perform OCR
    # The OCR text might take several seconds per page.
    raw_sanskrit_text = pytesseract.image_to_string(img, lang=OCR_LANG)
    
    # 4. Clean text before translation
    # Remove awkward excessive whitespaces that OCR might introduce
    cleaned_text = " ".join(raw_sanskrit_text.split())
    
    if not cleaned_text:
         return raw_sanskrit_text, "(No text found on this page)"

    # 5. Translate text
    # GoogleTranslator handles chunks under ~5000 characters automatically.
    # Translating from 'sa' (Sanskrit) to 'en' (English).
    retries = 3
    translated_text = "[Translation Failed / Empty]"
    for attempt in range(retries):
        try:
            translated_text = translator.translate(cleaned_text)
            break
        except Exception as e:
            error_msg = str(e)
            print(f"[!] Translation Error (attempt {attempt+1}/{retries}): {error_msg}", file=sys.stderr)
            
            # Hard-failing specific errors that won't benefit from retries
            if "No translation was found" in error_msg:
                translated_text = "[Translation Error: Google Translate returned empty for this text]"
                break
                
            if attempt < retries - 1:
                print("Sleeping for 60 seconds before retrying...")
                time.sleep(60)
            else:
                print("Rate limit exceeded persistently. Exiting so you can resume later.", file=sys.stderr)
                sys.exit(1)

    return raw_sanskrit_text, translated_text


def main():
    if not os.path.exists(PDF_FILE_PATH):
        print(f"Error: Could not find '{PDF_FILE_PATH}'.", file=sys.stderr)
        return

    print("Opening the PDF...", PDF_FILE_PATH)
    doc = fitz.open(PDF_FILE_PATH)
    
    # Check total pages
    total_pages = len(doc)
    print(f"Total pages in document: {total_pages}")
    
    # Assuming START_PAGE is 1-indexed, we convert to 0-indexed index.
    start_index = START_PAGE - 1
    
    # Check output file to see where we left off
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            # Find all numbers following "PAGE " at the beginning of a line
            matches = re.findall(r"^PAGE (\d+)$", content, re.MULTILINE)
            if matches:
                last_processed_page = int(matches[-1])
                print(f"Found existing progress up to Page {last_processed_page}.")
                start_index = max(start_index, last_processed_page)
    
    if start_index >= total_pages or start_index < 0:
        print("Error: Starting page index is out of bounds.", file=sys.stderr)
        return
        
    print(f"Starting extraction and translation from Page {start_index + 1}...")

    translator = GoogleTranslator(source='sa', target='en')
    
    # Open the output file in append mode.
    # This ensures that progress is saved continuously in case of an interruption.
    with open(OUTPUT_FILE, "a", encoding="utf-8") as out_file:
        
        for i in range(start_index, total_pages):
            page_number = i + 1
            print(f"--- Processing Page {page_number} / {total_pages} ---")
            page = doc.load_page(i)
            
            sanskrit_text, english_text = process_and_translate_page(page, translator)
            
            # Write to our output file
            out_file.write(f"\n{'='*40}\n")
            out_file.write(f"PAGE {page_number}\n")
            out_file.write(f"{'='*40}\n\n")
            
            out_file.write("--- ORIGINAL SANSKRIT VOCABULAR (OCR) ---\n")
            out_file.write(sanskrit_text.strip() + "\n\n")
            
            out_file.write("--- ENGLISH TRANSLATION ---\n")
            out_file.write(english_text.strip() + "\n\n")
            out_file.flush() # Force write to disk immediately
            
            print(f"Page {page_number} completed. Short preview of translation:\n{english_text[:100]}...\n")
            
            # Add a small delay so we do not flood the translation API
            time.sleep(1.5)

    print("--- Translation Completed ---")
    print(f"Results saved to '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()
