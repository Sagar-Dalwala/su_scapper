"""
Core functionality for PDF to DOCX conversion with formatting preserved.
"""
import sys
import logging
from pathlib import Path
import PyPDF2
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.enum.section import WD_ORIENT
from pdf2docx import Converter

# Get logger
logger = logging.getLogger(__name__)

def convert_pdf_to_docx_with_pdf2docx(pdf_path, docx_path):
    """
    Convert PDF to DOCX using pdf2docx package which preserves formatting better.
    This is similar to how ilovepdf maintains formatting during conversion.
    
    Args:
        pdf_path: Path to the PDF file
        docx_path: Path where to save the DOCX file
        
    Returns:
        bool: True if conversion was successful, False otherwise
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

def create_docx_from_pdf_text(pdf_path, docx_path):
    """
    Fallback method to create a DOCX file from PDF text extraction.
    Not as good as pdf2docx but works as a fallback.
    
    Args:
        pdf_path: Path to the PDF file
        docx_path: Path where to save the DOCX file
        
    Returns:
        bool: True if conversion was successful, False otherwise
    """
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

def convert_with_fallback(pdf_path, docx_path):
    """
    Try to convert using primary method, fall back to secondary if needed.
    
    Args:
        pdf_path: Path to the PDF file
        docx_path: Path where to save the DOCX file
        
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    # First attempt: use pdf2docx which maintains better formatting
    success = convert_pdf_to_docx_with_pdf2docx(pdf_path, docx_path)
    
    if not success:
        logger.warning(f"Primary conversion method failed for {pdf_path}, trying fallback method")
        success = create_docx_from_pdf_text(pdf_path, docx_path)
    
    return success 