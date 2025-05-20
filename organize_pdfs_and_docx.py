#!/usr/bin/env python3
"""
This script organizes PDFs and DOCX files in a directory.
It moves PDF files to a 'pdfs' folder and DOCX files to a 'pdf_to_docx' folder.
"""

import os
import sys
import shutil
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("organize_files.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def organize_files(directory, pdf_folder="pdfs", docx_folder="pdf_to_docx", recursive=False):
    """
    Organize PDF and DOCX files into separate folders
    
    Args:
        directory: Base directory to organize
        pdf_folder: Folder name for PDF files
        docx_folder: Folder name for DOCX files
        recursive: Whether to process subdirectories recursively
    
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
    
    # Find files
    if recursive:
        # Use rglob for recursive search
        pdf_files = list(directory.rglob("*.pdf"))
        docx_files = list(directory.rglob("*.docx"))
    else:
        # Use glob for non-recursive search
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
    parser = argparse.ArgumentParser(description='Organize PDF and DOCX files into separate folders')
    parser.add_argument('directory', nargs='?', default='.', 
                        help='Directory to organize (default: current directory)')
    parser.add_argument('--pdf-folder', default='pdfs', 
                        help='Folder name for PDF files (default: pdfs)')
    parser.add_argument('--docx-folder', default='pdf_to_docx', 
                        help='Folder name for DOCX files (default: pdf_to_docx)')
    parser.add_argument('--recursive', '-r', action='store_true', 
                        help='Process subdirectories recursively')
    
    args = parser.parse_args()
    
    directory = Path(args.directory)
    
    if not directory.exists() or not directory.is_dir():
        logger.error(f"Directory not found: {directory}")
        sys.exit(1)
    
    logger.info(f"Organizing files in {directory}")
    pdf_count, docx_count = organize_files(
        directory, 
        args.pdf_folder, 
        args.docx_folder, 
        args.recursive
    )
    
    logger.info(f"Organization complete! Moved {pdf_count} PDF files and {docx_count} DOCX files")
    print(f"\nOrganization complete!")
    print(f"- Moved {pdf_count} PDF files to {args.pdf_folder}/")
    print(f"- Moved {docx_count} DOCX files to {args.docx_folder}/")

if __name__ == "__main__":
    main() 