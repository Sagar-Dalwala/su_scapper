import os
import pandas as pd
import PyPDF2
import tabula
from pathlib import Path
import re
import numpy as np
from tqdm import tqdm
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pdf_conversion.log"),
        logging.StreamHandler()
    ]
)

class PDFToCSVConverter:
    def __init__(self, input_dir='output/pdfs', output_dir='csv_output'):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text content from PDF using PyPDF2"""
        text_content = []
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text = page.extract_text()
                        if text:
                            text_content.append(f"Page {page_num+1}: {text}")
                    except Exception as e:
                        logging.warning(f"Error extracting text from page {page_num+1} in {pdf_path}: {str(e)}")
            return '\n'.join(text_content)
        except Exception as e:
            logging.error(f"Error opening PDF {pdf_path}: {str(e)}")
            return ""
    
    def extract_tables_from_pdf(self, pdf_path):
        """Extract tables from PDF using tabula-py"""
        try:
            # Try to use tabula to extract tables
            tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
            return tables
        except Exception as e:
            logging.warning(f"Error extracting tables from {pdf_path}: {str(e)}")
            return []
    
    def clean_text(self, text):
        """Clean and format extracted text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
        return text.strip()
    
    def parse_syllabus_structure(self, text):
        """
        Attempt to parse the syllabus structure into sections like:
        - Course title
        - Course description
        - Course objectives
        - Learning outcomes
        - Units/modules
        - Assessment methods
        """
        sections = {}
        
        # Common section headers in syllabi
        section_patterns = [
            (r'course(?:\s+code|\s+title)?[\s:]+([^\n]+)', 'course_title'),
            (r'course\s+description[\s:]+([^\n]+)', 'description'),
            (r'(?:course\s+)?objectives?[\s:]+(.+?)(?=\n\s*\n|\n\s*[A-Z]|\Z)', 'objectives'),
            (r'learning\s+outcomes?[\s:]+(.+?)(?=\n\s*\n|\n\s*[A-Z]|\Z)', 'learning_outcomes'),
            (r'(?:unit|module)\s*(\d+)[\s:]+([^\n]+)', 'unit'),
            (r'assessment[\s:]+(.+?)(?=\n\s*\n|\n\s*[A-Z]|\Z)', 'assessment'),
            (r'reference(?:s)?[\s:]+(.+?)(?=\n\s*\n|\n\s*[A-Z]|\Z)', 'references'),
        ]
        
        for pattern, key in section_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if key == 'unit':
                    unit_num = match.group(1)
                    unit_title = match.group(2).strip()
                    if 'units' not in sections:
                        sections['units'] = {}
                    sections['units'][f'Unit {unit_num}'] = unit_title
                else:
                    sections[key] = match.group(1).strip()
                    
        return sections
    
    def process_pdf(self, pdf_path):
        """Process a single PDF file and convert it to CSV"""
        try:
            logging.info(f"Processing {pdf_path}")
            
            # Extract text content
            text_content = self.extract_text_from_pdf(pdf_path)
            if not text_content:
                logging.error(f"No text content extracted from {pdf_path}")
                return False
                
            # Try to parse syllabus structure
            syllabus_sections = self.parse_syllabus_structure(text_content)
            
            # Create a basic DataFrame with the raw text content by page
            text_rows = []
            for line in text_content.split('\n'):
                if line.strip():
                    page_match = re.match(r'Page (\d+):(.*)', line)
                    if page_match:
                        page_num = page_match.group(1)
                        content = page_match.group(2).strip()
                        if content:
                            text_rows.append({
                                'page': int(page_num),
                                'content_type': 'text',
                                'content': self.clean_text(content)
                            })
            
            # Extract tables
            tables = self.extract_tables_from_pdf(pdf_path)
            table_rows = []
            
            # Process each table
            for i, table in enumerate(tables):
                if not table.empty:
                    # Convert table to string representation
                    table_str = table.to_string(index=False)
                    table_rows.append({
                        'page': i+1,  # Approximate page number
                        'content_type': 'table',
                        'content': table_str
                    })
            
            # Combine text and table rows
            all_rows = text_rows + table_rows
            
            # Create a structured DataFrame for the syllabus
            structured_rows = []
            
            # Add syllabus structure info if available
            for section, content in syllabus_sections.items():
                if section == 'units' and isinstance(content, dict):
                    for unit_name, unit_content in content.items():
                        structured_rows.append({
                            'section': 'Unit',
                            'subsection': unit_name,
                            'content': unit_content
                        })
                else:
                    structured_rows.append({
                        'section': section.replace('_', ' ').title(),
                        'subsection': '',
                        'content': content
                    })
            
            # Create DataFrames
            df_raw = pd.DataFrame(all_rows)
            df_structured = pd.DataFrame(structured_rows) if structured_rows else None
            
            # Generate output filenames
            base_filename = Path(pdf_path).stem
            raw_output = os.path.join(self.output_dir, f"{base_filename}_raw.csv")
            structured_output = os.path.join(self.output_dir, f"{base_filename}_structured.csv")
            
            # Save to CSV
            if not df_raw.empty:
                df_raw.to_csv(raw_output, index=False, encoding='utf-8')
                logging.info(f"Raw content saved to {raw_output}")
                
            if df_structured is not None and not df_structured.empty:
                df_structured.to_csv(structured_output, index=False, encoding='utf-8')
                logging.info(f"Structured content saved to {structured_output}")
            
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
        
        for pdf_file in tqdm(pdf_files, desc="Converting PDFs"):
            pdf_path = os.path.join(self.input_dir, pdf_file)
            if self.process_pdf(pdf_path):
                successful += 1
            else:
                failed += 1
        
        logging.info(f"\nConversion Summary:")
        logging.info(f"Successfully converted: {successful} files")
        logging.info(f"Failed conversions: {failed} files")

def main():
    converter = PDFToCSVConverter()
    converter.process_all_pdfs()

if __name__ == "__main__":
    main() 