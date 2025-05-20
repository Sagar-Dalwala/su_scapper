#!/usr/bin/env python3
import os
import sys
import logging
import argparse
import shutil
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

# Try to import from the package, but fall back to direct import if not installed
try:
    from enhanced_pdf_to_docx import convert_with_fallback
except ImportError:
    # Direct import from script
    from enhanced_pdf_to_docx import convert_with_fallback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("batch_pdf_to_docx_conversion.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def process_file(pdf_path, output_dir=None, keep_structure=False):
    """
    Process a single PDF file for conversion
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the output file (or None to use same directory)
        keep_structure: Whether to keep the directory structure in output_dir
    
    Returns:
        tuple: (pdf_path, success, output_path)
    """
    pdf_path = Path(pdf_path)
    
    # Determine output path
    if output_dir:
        output_dir = Path(output_dir)
        
        if keep_structure and pdf_path.is_absolute():
            # Preserve directory structure relative to working dir
            rel_path = pdf_path.relative_to(Path.cwd())
            # Remove the filename and join with output_dir
            rel_dir = rel_path.parent
            output_path = output_dir / rel_dir / f"{pdf_path.stem}.docx"
        else:
            # Just use the filename in the output directory
            output_path = output_dir / f"{pdf_path.stem}.docx"
    else:
        # Default: same directory as PDF
        output_path = pdf_path.with_suffix('.docx')
    
    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Perform conversion
    logger.info(f"Converting: {pdf_path} -> {output_path}")
    success = convert_with_fallback(pdf_path, output_path)
    
    return pdf_path, success, output_path

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
    
    # Find files (only in current directory, not in subdirectories)
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
    """Batch convert PDF files to DOCX format with preserved formatting"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("batch_pdf_to_docx_conversion.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    parser = argparse.ArgumentParser(description='Batch convert PDF files to DOCX with preserved formatting')
    parser.add_argument('input', help='Input PDF file or directory of PDF files')
    parser.add_argument('--output-dir', '-o', help='Output directory for DOCX files')
    parser.add_argument('--recursive', '-r', action='store_true', help='Recursively process directories')
    parser.add_argument('--keep-structure', '-k', action='store_true', 
                        help='Keep directory structure in output directory')
    parser.add_argument('--workers', '-w', type=int, default=os.cpu_count(), 
                        help='Number of parallel workers')
    parser.add_argument('--organize', action='store_true',
                        help='Organize files into separate PDF and DOCX folders after conversion')
    parser.add_argument('--pdf-folder', default='pdfs',
                        help='Folder name for PDF files when organizing (default: pdfs)')
    parser.add_argument('--docx-folder', default='pdf_to_docx',
                        help='Folder name for DOCX files when organizing (default: pdf_to_docx)')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    # Collect all PDF files to process
    pdf_files = []
    
    if input_path.is_file():
        if input_path.suffix.lower() == '.pdf':
            pdf_files.append(input_path)
        else:
            logger.error(f"Input file is not a PDF: {input_path}")
            sys.exit(1)
    elif input_path.is_dir():
        if args.recursive:
            # Walk through all subdirectories
            pattern = '**/*.pdf'
        else:
            # Only check files in the top directory
            pattern = '*.pdf'
            
        pdf_files = list(input_path.glob(pattern))
        logger.info(f"Found {len(pdf_files)} PDF files to process")
    else:
        logger.error(f"Input path not found: {input_path}")
        sys.exit(1)
    
    if not pdf_files:
        logger.error("No PDF files found")
        sys.exit(1)
    
    # Create output directory if specified
    if args.output_dir:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = None
    
    # Process files in parallel
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = []
        for pdf_file in pdf_files:
            future = executor.submit(
                process_file, 
                pdf_file, 
                output_dir,
                args.keep_structure
            )
            futures.append(future)
        
        # Collect results as they complete
        for future in as_completed(futures):
            try:
                pdf_path, success, output_path = future.result()
                results.append((pdf_path, success, output_path))
                
                status = "SUCCESS" if success else "FAILED"
                logger.info(f"{status}: {pdf_path} -> {output_path}")
            except Exception as e:
                logger.error(f"Error processing task: {str(e)}")
    
    # Summarize results
    successful = sum(1 for _, success, _ in results if success)
    failed = len(results) - successful
    
    logger.info(f"Conversion summary: {successful} successful, {failed} failed")
    
    # List failed conversions if any
    if failed > 0:
        logger.info("Failed conversions:")
        for pdf_path, success, _ in results:
            if not success:
                logger.info(f"  - {pdf_path}")
    
    # Organize files if requested
    if args.organize:
        if args.output_dir:
            organize_dir = output_dir
        else:
            # If no output dir specified, organize files in the input directory
            # (if it's a directory) or the parent of the input file
            if input_path.is_dir():
                organize_dir = input_path
            else:
                organize_dir = input_path.parent
        
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
    
    if failed == 0:
        logger.info("All conversions completed successfully!")

if __name__ == "__main__":
    main() 