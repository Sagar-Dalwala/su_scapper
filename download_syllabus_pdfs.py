#!/usr/bin/env python3
"""
SRKI Syllabus PDF Downloader

This script runs the syllabus scraper and then the PDF downloader
to extract and download all syllabus PDFs from the SRKI website.
"""

import os
import sys
import argparse
import subprocess
import time

def print_header():
    """Print a header for the script."""
    print("\n" + "="*70)
    print("                 SRKI SYLLABUS PDF DOWNLOADER")
    print("="*70 + "\n")

def run_enhanced_scraper(output_dir, headless=False):
    """Run the enhanced syllabus scraper."""
    print("Step 1: Running Enhanced Syllabus Scraper...")
    
    try:
        from enhanced_syllabus_scraper import EnhancedSyllabusScraper
        
        # Create and run the scraper
        scraper = EnhancedSyllabusScraper(output_dir=output_dir)
        
        # Set headless mode if requested
        if headless:
            scraper.chrome_options.add_argument("--headless")
            # Re-initialize the driver with headless option
            scraper.driver.quit()
            scraper.driver = scraper.driver.__class__(
                service=scraper.driver.service,
                options=scraper.chrome_options
            )
        
        # Run the scraper
        scraper.scrape_syllabus()
        
        # Clean up
        scraper.driver.quit()
        
        csv_path = os.path.join(output_dir, "syllabus_links.csv")
        if os.path.exists(csv_path):
            print(f"Scraper completed successfully. Syllabus links saved to {csv_path}")
            return csv_path
        else:
            print("Error: Scraper did not generate the expected CSV file.")
            return None
    
    except Exception as e:
        print(f"Error running enhanced scraper: {str(e)}")
        return None

def run_pdf_downloader(input_file, output_dir, headless=False):
    """Run the specialized PDF downloader."""
    print("\nStep 2: Running Specialized PDF Downloader...")
    
    try:
        from pdf_downloader import PDFDownloader
        
        # Create and run the downloader
        downloader = PDFDownloader(output_dir=output_dir, headless=headless)
        downloader.download_pdfs_from_file(input_file)
        
        # Clean up
        downloader.cleanup()
        
        print("PDF Downloader completed.")
        return True
    
    except Exception as e:
        print(f"Error running PDF downloader: {str(e)}")
        return False

def main():
    """Main function to parse arguments and run the tools."""
    print_header()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Download syllabus PDFs from SRKI website.')
    
    parser.add_argument('--output', '-o', default='output',
                        help='Output directory for scraped data and PDFs (default: output)')
    
    parser.add_argument('--skip-scrape', '-s', action='store_true',
                        help='Skip the scraping step and use existing CSV file')
    
    parser.add_argument('--input', '-i',
                        help='Input CSV file with PDF links (only used with --skip-scrape)')
    
    parser.add_argument('--headless', action='store_true',
                        help='Run browser in headless mode (no UI)')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    
    # Step 1: Run the scraper (unless skipped)
    csv_path = None
    if args.skip_scrape:
        if args.input:
            csv_path = args.input
            print(f"Skipping scrape step. Using existing file: {csv_path}")
        else:
            print("Error: --input is required when using --skip-scrape")
            parser.print_help()
            return 1
    else:
        csv_path = run_enhanced_scraper(args.output, args.headless)
        
        if not csv_path:
            print("Error: Failed to generate syllabus links CSV.")
            return 1
    
    # Step 2: Run the PDF downloader
    success = run_pdf_downloader(csv_path, args.output, args.headless)
    
    if success:
        pdf_dir = os.path.join(args.output, "pdfs")
        pdf_count = len([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]) if os.path.exists(pdf_dir) else 0
        
        print("\n" + "="*70)
        print(f"Process completed. {pdf_count} PDFs downloaded to {pdf_dir}")
        print("="*70)
        return 0
    else:
        print("\nError: PDF download process failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 