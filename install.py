#!/usr/bin/env python3
"""
Installation script for the Enhanced PDF to DOCX converter.
This script installs:
1. All required dependencies
2. The enhanced_pdf_to_docx package with command-line tools

Usage:
    python install.py
"""

import os
import sys
import subprocess
import platform

def main():
    print("Installing Enhanced PDF to DOCX Converter...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)
    
    # Install requirements
    print("\nInstalling dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        print("Error: Failed to install dependencies")
        sys.exit(1)
    
    # Install the package
    print("\nInstalling enhanced-pdf-to-docx...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
    except subprocess.CalledProcessError:
        print("Error: Failed to install package")
        sys.exit(1)
    
    # Verify installation
    print("\nVerifying installation...")
    try:
        from enhanced_pdf_to_docx import __version__
        print(f"Successfully installed enhanced-pdf-to-docx version {__version__}")
    except ImportError:
        print("Error: Package installation verification failed")
        sys.exit(1)
    
    # Installation complete!
    print("\n✅ Installation complete!")
    print("\nYou can now use the following commands:")
    print("  pdf-to-docx [pdf_file] - Convert a single PDF file to DOCX")
    print("  batch-pdf-to-docx [directory] - Convert multiple PDF files to DOCX")
    print("\nFor more information, run:")
    print("  pdf-to-docx --help")
    print("  batch-pdf-to-docx --help")
    
    # If Windows, add note about command availability
    if platform.system() == 'Windows':
        print("\nNote for Windows users: You may need to restart your command prompt")
        print("or use the full path to access the commands.")

if __name__ == "__main__":
    main() 