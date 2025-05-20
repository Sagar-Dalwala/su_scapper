import os
import sys
import logging
from pathlib import Path
import subprocess
import argparse
import tempfile
import shutil
from pdf2docx import Converter
import PyPDF2
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn
from docx.enum.section import WD_SECTION
from docx.enum.section import WD_ORIENT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("enhanced_pdf_to_docx_conversion.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def convert_pdf_to_docx_with_pdf2docx(pdf_path, docx_path):
    """
    Convert PDF to DOCX using pdf2docx package which preserves formatting better
    This is similar to how ilovepdf maintains formatting during conversion
    """
    try:
        # Using pdf2docx for high-quality conversion with formatting preserved
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()
        
        logger.info(f"Successfully converted {pdf_path} to {docx_path}")
        return True
    except Exception as e:
        logger.error(f"Error converting {pdf_path} with pdf2docx: {str(e)}")
        return False

def convert_with_fallback(pdf_path, docx_path):
    """
    Try to convert using primary method, fall back to secondary if needed
    """
    # First attempt: use pdf2docx which maintains better formatting
    success = convert_pdf_to_docx_with_pdf2docx(pdf_path, docx_path)
    
    if not success:
        logger.warning(f"Primary conversion method failed for {pdf_path}, trying fallback method")
        try:
            # Fallback method - extract text and create simple docx
            doc = Document()
            
            # Set document properties to match PDF source
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                
                # Try to detect PDF page size and orientation
                if len(pdf_reader.pages) > 0:
                    page = pdf_reader.pages[0]
                    width = float(page.mediabox.width)
                    height = float(page.mediabox.height)
                    
                    # Set document page size to match PDF
                    section = doc.sections[0]
                    section.page_width = Pt(width)
                    section.page_height = Pt(height)
                    
                    # Set orientation
                    if width > height:
                        section.orientation = WD_ORIENT.LANDSCAPE
                    else:
                        section.orientation = WD_ORIENT.PORTRAIT
                
                # Extract text from each page and add to document
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    # Add content
                    if page_num > 0:
                        doc.add_section(WD_SECTION.NEW_PAGE)
                    
                    # Add the text
                    para = doc.add_paragraph(text)
            
            # Save the document
            doc.save(docx_path)
            logger.info(f"Successfully converted {pdf_path} to {docx_path} using fallback method")
            return True
        except Exception as e:
            logger.error(f"Fallback conversion method also failed for {pdf_path}: {str(e)}")
            return False
    
    return success

def organize_files(directory, pdf_folder="pdfs", docx_folder="pdf_to_docx"):
    """
    Organize PDF and DOCX files into separate folders
    
    Args:
        directory: Base directory to organize
        pdf_folder: Folder name for PDF files
        docx_folder: Folder name for DOCX files
    
    Returns:
        tuple: (pdf_count, docx_count) - Number of files moved
    """
    directory = Path(directory)
    
    # Create target folders if they don't exist
    pdf_dir = directory / pdf_folder
    docx_dir = directory / docx_folder
    
    pdf_dir.mkdir(exist_ok=True)
    docx_dir.mkdir(exist_ok=True)
    
    # Track number of files moved
    pdf_count = 0
    docx_count = 0
    
    # Find files in the current directory
    pdf_files = list(directory.glob("*.pdf"))
    docx_files = list(directory.glob("*.docx"))
    
    # Filter out files that are already in target directories
    pdf_files = [f for f in pdf_files if pdf_folder not in f.parts and docx_folder not in f.parts]
    docx_files = [f for f in docx_files if pdf_folder not in f.parts and docx_folder not in f.parts]
    
    logger.info(f"Found {len(pdf_files)} PDF files and {len(docx_files)} DOCX files to organize")
    
    # Move PDF files
    for pdf_file in pdf_files:
        dest_file = pdf_dir / pdf_file.name
        
        # Check if destination file already exists
        if dest_file.exists():
            logger.warning(f"Skipping {pdf_file} - file already exists in destination")
            continue
            
        try:
            shutil.move(str(pdf_file), str(dest_file))
            logger.info(f"Moved PDF: {pdf_file} -> {dest_file}")
            pdf_count += 1
        except Exception as e:
            logger.error(f"Failed to move {pdf_file}: {str(e)}")
    
    # Move DOCX files
    for docx_file in docx_files:
        dest_file = docx_dir / docx_file.name
        
        # Check if destination file already exists
        if dest_file.exists():
            logger.warning(f"Skipping {docx_file} - file already exists in destination")
            continue
            
        try:
            shutil.move(str(docx_file), str(dest_file))
            logger.info(f"Moved DOCX: {docx_file} -> {dest_file}")
            docx_count += 1
        except Exception as e:
            logger.error(f"Failed to move {docx_file}: {str(e)}")
    
    return pdf_count, docx_count

def main():
    """
    Convert PDF to DOCX with formatting preserved (similar to ilovepdf)
    """
    parser = argparse.ArgumentParser(description='Convert PDF to DOCX with preserved formatting')
    parser.add_argument('pdf_path', help='Path to the input PDF file')
    parser.add_argument('--output', '-o', help='Path to the output DOCX file (optional)')
    parser.add_argument('--organize', action='store_true',
                        help='Organize files into separate PDF and DOCX folders after conversion')
    parser.add_argument('--pdf-folder', default='pdfs',
                        help='Folder name for PDF files when organizing (default: pdfs)')
    parser.add_argument('--docx-folder', default='pdf_to_docx',
                        help='Folder name for DOCX files when organizing (default: pdf_to_docx)')
    
    args = parser.parse_args()
    
    pdf_path = Path(args.pdf_path)
    
    if not pdf_path.exists():
        logger.error(f"PDF file not found: {pdf_path}")
        sys.exit(1)
    
    # Determine output path
    if args.output:
        docx_path = Path(args.output)
    else:
        docx_path = pdf_path.with_suffix('.docx')
    
    # Ensure the output directory exists
    docx_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert the file
    logger.info(f"Starting conversion of {pdf_path} to {docx_path}")
    success = convert_with_fallback(pdf_path, docx_path)
    
    if success:
        logger.info(f"Conversion complete! Output saved to {docx_path}")
        
        # Organize files if requested
        if args.organize:
            organize_dir = pdf_path.parent
            logger.info(f"Organizing files in {organize_dir}")
            pdf_count, docx_count = organize_files(
                organize_dir,
                args.pdf_folder,
                args.docx_folder
            )
            logger.info(f"Organization complete! Moved {pdf_count} PDF files and {docx_count} DOCX files")
            print(f"\nOrganized files into separate folders:")
            print(f"- Moved {pdf_count} PDF files to {args.pdf_folder}/")
            print(f"- Moved {docx_count} DOCX files to {args.docx_folder}/")
    else:
        logger.error(f"Failed to convert {pdf_path}")
        sys.exit(1)

if __name__ == "__main__":
    main() 