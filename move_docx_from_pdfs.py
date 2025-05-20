#!/usr/bin/env python3
"""
This script moves all DOCX files from output/pdfs folder to output/pdf_to_docx folder.
"""

import os
import sys
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("move_docx_files.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def move_docx_files(source_dir="output/pdfs", target_dir="output/pdf_to_docx"):
    """
    Move all DOCX files from source_dir to target_dir
    
    Args:
        source_dir: Source directory containing DOCX files to move
        target_dir: Target directory where to move DOCX files
    
    Returns:
        int: Number of files moved
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # Check if source directory exists
    if not source_path.exists() or not source_path.is_dir():
        logger.error(f"Source directory not found: {source_path}")
        return 0
    
    # Create target directory if it doesn't exist
    target_path.mkdir(parents=True, exist_ok=True)
    
    # Find all DOCX files in source directory
    docx_files = list(source_path.glob("*.docx"))
    
    if not docx_files:
        logger.info(f"No DOCX files found in {source_path}")
        return 0
    
    logger.info(f"Found {len(docx_files)} DOCX files to move")
    
    # Move each DOCX file to target directory
    moved_count = 0
    for docx_file in docx_files:
        dest_file = target_path / docx_file.name
        
        # Check if destination file already exists
        if dest_file.exists():
            logger.warning(f"Skipping {docx_file.name} - file already exists in destination")
            continue
            
        try:
            shutil.move(str(docx_file), str(dest_file))
            logger.info(f"Moved: {docx_file} -> {dest_file}")
            moved_count += 1
        except Exception as e:
            logger.error(f"Failed to move {docx_file}: {str(e)}")
    
    return moved_count

def main():
    # Default directories
    source_dir = "output/pdfs"
    target_dir = "output/pdf_to_docx"
    
    # Allow custom directories via command line arguments
    if len(sys.argv) > 1:
        source_dir = sys.argv[1]
    if len(sys.argv) > 2:
        target_dir = sys.argv[2]
    
    print(f"Moving DOCX files from '{source_dir}' to '{target_dir}'...")
    
    # Move the files
    moved_count = move_docx_files(source_dir, target_dir)
    
    # Print summary
    if moved_count > 0:
        print(f"\nSuccess! Moved {moved_count} DOCX files to {target_dir}")
    else:
        print(f"\nNo DOCX files were moved. Check if there are any DOCX files in {source_dir}")

if __name__ == "__main__":
    main() 