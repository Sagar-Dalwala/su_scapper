"""
Enhanced PDF to DOCX Converter
==============================

This package provides tools to convert PDF files to DOCX format while
preserving the original formatting, similar to how ilovepdf.com works.
"""

import sys
import logging
from pathlib import Path

from .converter import convert_pdf_to_docx_with_pdf2docx, convert_with_fallback

__version__ = '1.0.0'

def main():
    """
    Main entry point for the PDF to DOCX converter
    """
    # Defer imports to reduce startup time when used as a library
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert PDF to DOCX with preserved formatting')
    parser.add_argument('pdf_path', help='Path to the input PDF file')
    parser.add_argument('--output', '-o', help='Path to the output DOCX file (optional)')
    
    args = parser.parse_args()
    
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
    else:
        logger.error(f"Failed to convert {pdf_path}")
        sys.exit(1) 