import os
import PyPDF2
from tqdm import tqdm
import logging
import re
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pdf_extraction.log"),
        logging.StreamHandler()
    ]
)

class PDFTextExtractor:
    def __init__(self, input_dir='output/pdfs', output_dir='extracted_text'):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def extract_text_with_pypdf2(self, pdf_path):
        """Extract text content from PDF using PyPDF2"""
        text_content = []
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                # Add PDF metadata if available
                metadata = pdf_reader.metadata
                if metadata:
                    text_content.append("---- PDF METADATA ----")
                    for key, value in metadata.items():
                        if key and value:
                            # Remove the leading slash from keys
                            clean_key = key[1:] if key.startswith('/') else key
                            text_content.append(f"{clean_key}: {value}")
                    text_content.append("---- END METADATA ----\n")
                
                text_content.append(f"Total Pages: {total_pages}\n")
                
                # Extract text from each page
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text = page.extract_text()
                        if text and text.strip():
                            text_content.append(f"==== PAGE {page_num+1} ====")
                            text_content.append(text)
                            text_content.append("")  # Empty line for separation
                        else:
                            text_content.append(f"==== PAGE {page_num+1} ====")
                            text_content.append("[No extractable text found on this page]")
                            text_content.append("")
                    except Exception as e:
                        logging.warning(f"Error extracting text from page {page_num+1} in {pdf_path}: {str(e)}")
                        text_content.append(f"==== PAGE {page_num+1} ====")
                        text_content.append(f"[Error extracting text: {str(e)}]")
                        text_content.append("")
            
            return '\n'.join(text_content)
        except Exception as e:
            logging.error(f"Error opening PDF {pdf_path}: {str(e)}")
            return ""
    
    def extract_text_with_pdfplumber(self, pdf_path):
        """Extract text using pdfplumber (as an alternative to PyPDF2)"""
        try:
            import pdfplumber
            text_content = []
            
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                text_content.append(f"Total Pages: {total_pages}\n")
                
                for page_num, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text()
                        if text and text.strip():
                            text_content.append(f"==== PAGE {page_num+1} ====")
                            text_content.append(text)
                            text_content.append("")  # Empty line for separation
                        else:
                            text_content.append(f"==== PAGE {page_num+1} ====")
                            text_content.append("[No extractable text found on this page]")
                            text_content.append("")
                    except Exception as e:
                        logging.warning(f"Error extracting text from page {page_num+1} with pdfplumber: {str(e)}")
                        text_content.append(f"==== PAGE {page_num+1} ====")
                        text_content.append(f"[Error extracting text: {str(e)}]")
                        text_content.append("")
            
            return '\n'.join(text_content)
        except ImportError:
            logging.warning("pdfplumber not installed. Falling back to PyPDF2.")
            return self.extract_text_with_pypdf2(pdf_path)
        except Exception as e:
            logging.error(f"Error using pdfplumber on {pdf_path}: {str(e)}")
            return self.extract_text_with_pypdf2(pdf_path)
    
    def process_pdf(self, pdf_path):
        """Process a single PDF file and extract text to a .txt file"""
        try:
            logging.info(f"Processing {pdf_path}")
            
            # Try with PyPDF2 first
            text_content = self.extract_text_with_pypdf2(pdf_path)
            
            # If PyPDF2 fails or extracts minimal text, try with pdfplumber
            if not text_content or len(text_content.strip()) < 100:
                logging.info(f"Minimal text extracted with PyPDF2, trying pdfplumber for {pdf_path}")
                text_content = self.extract_text_with_pdfplumber(pdf_path)
            
            if not text_content:
                logging.error(f"No text content extracted from {pdf_path}")
                return False
            
            # Generate output filename
            output_filename = os.path.join(
                self.output_dir,
                f"{Path(pdf_path).stem}.txt"
            )
            
            # Save to text file
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            logging.info(f"Successfully extracted text from {pdf_path} to {output_filename}")
            return True
            
        except Exception as e:
            logging.error(f"Error processing {pdf_path}: {str(e)}")
            return False
    
    def process_all_pdfs(self):
        """Process all PDF files in the input directory"""
        pdf_files = [f for f in os.listdir(self.input_dir) if f.lower().endswith('.pdf')]
        logging.info(f"Found {len(pdf_files)} PDF files to process")
        
        successful = 0
        failed = 0
        
        for pdf_file in tqdm(pdf_files, desc="Extracting text from PDFs"):
            pdf_path = os.path.join(self.input_dir, pdf_file)
            if self.process_pdf(pdf_path):
                successful += 1
            else:
                failed += 1
        
        logging.info(f"\nExtraction Summary:")
        logging.info(f"Successfully extracted: {successful} files")
        logging.info(f"Failed extractions: {failed} files")

def main():
    extractor = PDFTextExtractor()
    extractor.process_all_pdfs()

if __name__ == "__main__":
    main() 