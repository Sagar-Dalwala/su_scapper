import os
import PyPDF2
import pdfplumber
from tqdm import tqdm
import logging
from pathlib import Path
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pdf_extraction.log"),
        logging.StreamHandler()
    ]
)

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF using multiple methods for better results"""
    try:
        # First try with PyPDF2
        text_content = []
        
        with open(pdf_path, 'rb') as file:
            # Extract with PyPDF2
            try:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Add document info
                text_content.append(f"DOCUMENT: {Path(pdf_path).stem}")
                text_content.append("-" * 50)
                
                # Extract text from each page
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text = page.extract_text()
                        if text and text.strip():
                            text_content.append(f"PAGE {page_num+1}:")
                            text_content.append(text)
                            text_content.append("")  # Empty line for separation
                    except Exception as e:
                        logging.warning(f"PyPDF2 error on page {page_num+1} in {pdf_path}: {str(e)}")
            except Exception as e:
                logging.warning(f"PyPDF2 extraction failed for {pdf_path}: {str(e)}")
        
        # Check if we got meaningful content
        full_text = '\n'.join(text_content)
        
        # If PyPDF2 extraction was insufficient, try with pdfplumber
        if len(full_text.strip()) < 100:
            logging.info(f"PyPDF2 extraction insufficient for {pdf_path}, trying pdfplumber")
            plumber_text = []
            
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    # Add document info again
                    plumber_text.append(f"DOCUMENT: {Path(pdf_path).stem}")
                    plumber_text.append("-" * 50)
                    
                    # Extract with pdfplumber
                    for page_num, page in enumerate(pdf.pages):
                        try:
                            text = page.extract_text()
                            if text and text.strip():
                                plumber_text.append(f"PAGE {page_num+1}:")
                                plumber_text.append(text)
                                plumber_text.append("")  # Empty line
                        except Exception as e:
                            logging.warning(f"Pdfplumber error on page {page_num+1}: {str(e)}")
                
                # If pdfplumber got better results, use them
                plumber_full_text = '\n'.join(plumber_text)
                if len(plumber_full_text.strip()) > len(full_text.strip()):
                    return plumber_full_text
            except Exception as e:
                logging.warning(f"Pdfplumber extraction failed for {pdf_path}: {str(e)}")
        
        return full_text
    
    except Exception as e:
        logging.error(f"Error extracting text from {pdf_path}: {str(e)}")
        return f"ERROR EXTRACTING {Path(pdf_path).stem}: {str(e)}"

def extract_and_combine(pdf_dir='output/pdfs', output_file='complete_syllabus_text.txt', limit=None):
    """Extract text from all PDFs and combine into a single file"""
    if not os.path.exists(pdf_dir):
        logging.error(f"Directory not found: {pdf_dir}")
        return
    
    # Create output directory if needed
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get list of PDF files
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    
    # Limit the number of files to process if specified
    if limit and isinstance(limit, int) and limit > 0:
        pdf_files = pdf_files[:limit]
        
    logging.info(f"Processing {len(pdf_files)} PDF files")
    
    # Extract and combine
    all_text = []
    
    for pdf_file in tqdm(pdf_files, desc="Extracting and combining PDFs"):
        pdf_path = os.path.join(pdf_dir, pdf_file)
        
        # Extract text
        text = extract_text_from_pdf(pdf_path)
        
        # Add to collection with separators
        all_text.append("\n\n" + "="*80 + "\n\n")
        all_text.append(text)
        all_text.append("\n\n")
    
    # Write combined content to file
    with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
        f.write(''.join(all_text))
    
    logging.info(f"Successfully created combined file: {output_file}")
    logging.info(f"Total size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")
    
    return output_file

if __name__ == "__main__":
    # Check if a limit is specified
    limit = None
    output_file = 'complete_syllabus_text.txt'
    
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
            logging.info(f"Limiting processing to {limit} files")
        except ValueError:
            logging.warning(f"Invalid limit value: {sys.argv[1]}, processing all files")
    
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
        
    extract_and_combine(limit=limit, output_file=output_file) 