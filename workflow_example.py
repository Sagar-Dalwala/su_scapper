#!/usr/bin/env python3
"""
Example workflow script that demonstrates the PDF to DOCX conversion
and automatic organization of files into separate folders.
"""

import os
import sys
import logging
from pathlib import Path
import argparse
import shutil
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("workflow_example.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """
    Run a complete workflow to convert PDF files and organize them
    """
    parser = argparse.ArgumentParser(description='Run a complete PDF to DOCX conversion workflow')
    parser.add_argument('input_dir', help='Directory containing PDF files')
    parser.add_argument('--pdf-folder', default='pdfs', help='Folder for PDF files')
    parser.add_argument('--docx-folder', default='pdf_to_docx', help='Folder for DOCX files')
    parser.add_argument('--workers', '-w', type=int, default=os.cpu_count(), 
                        help='Number of parallel workers')
    parser.add_argument('--recursive', '-r', action='store_true', 
                        help='Process subdirectories recursively')
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    
    if not input_dir.exists() or not input_dir.is_dir():
        logger.error(f"Input directory not found: {input_dir}")
        sys.exit(1)
    
    # STEP 1: Create the output folders if they don't exist
    pdf_dir = input_dir / args.pdf_folder
    docx_dir = input_dir / args.docx_folder
    
    pdf_dir.mkdir(exist_ok=True)
    docx_dir.mkdir(exist_ok=True)
    
    logger.info(f"Created output folders: {pdf_dir} and {docx_dir}")
    
    # STEP 2: Convert all PDFs to DOCX with batch processing
    logger.info("Starting batch conversion process...")
    
    cmd = [
        sys.executable,
        "batch_pdf_to_docx.py",
        str(input_dir),
        "--organize",
        f"--pdf-folder={args.pdf_folder}",
        f"--docx-folder={args.docx_folder}",
        f"--workers={args.workers}"
    ]
    
    if args.recursive:
        cmd.append("--recursive")
    
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        logger.error(f"Batch conversion failed with error code {e.returncode}")
        sys.exit(1)
    
    # STEP 3: Verify the results
    pdf_count = len(list(pdf_dir.glob("*.pdf")))
    docx_count = len(list(docx_dir.glob("*.docx")))
    
    logger.info("\nWorkflow Summary:")
    logger.info(f"- PDF files in {args.pdf_folder}: {pdf_count}")
    logger.info(f"- DOCX files in {args.docx_folder}: {docx_count}")
    
    print(f"\n✅ Workflow Complete!")
    print(f"- PDF files organized in: {pdf_dir}")
    print(f"- DOCX files organized in: {docx_dir}")
    print(f"- PDF count: {pdf_count}")
    print(f"- DOCX count: {docx_count}")
    
    if docx_count == 0:
        print("\n⚠️ Warning: No DOCX files were created. Check the logs for errors.")

if __name__ == "__main__":
    main() 