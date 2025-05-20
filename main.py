#!/usr/bin/env python3
"""
SRKI Website Scraper

This script provides a command-line interface to run different scrapers
for the Shree Ramkrishna Institute website.
"""

import argparse
import sys
import os

# Import scrapers
try:
    from enhanced_syllabus_scraper import EnhancedSyllabusScraper
    from full_site_scraper import SRKIWebsiteScraper
except ImportError:
    print("Error: Could not import scraper modules. Make sure they are in the same directory.")
    sys.exit(1)

def print_header():
    """Print a header for the script."""
    print("\n" + "="*70)
    print("                      SRKI WEBSITE SCRAPER")
    print("="*70 + "\n")

def setup_parser():
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(description='Scrape the SRKI website for syllabus and other content.')
    
    # Add arguments
    parser.add_argument('--type', '-t', choices=['syllabus', 'full'], default='syllabus',
                        help='Type of scraper to run (syllabus or full website)')
    
    parser.add_argument('--output', '-o', default='output',
                        help='Output directory for scraped data (default: output)')
    
    parser.add_argument('--download', '-d', action='store_true',
                        help='Download resources (PDFs, images) after scraping')
    
    parser.add_argument('--max-pages', '-m', type=int, default=50,
                        help='Maximum number of pages to crawl (for full website scraper)')
    
    parser.add_argument('--headless', action='store_true',
                        help='Run browser in headless mode (no UI)')
    
    return parser

def run_syllabus_scraper(args):
    """Run the syllabus scraper."""
    print("Running Syllabus Scraper...\n")
    
    # Create the scraper
    scraper = EnhancedSyllabusScraper(output_dir=args.output)
    
    # Set headless mode if requested
    if args.headless:
        scraper.chrome_options.add_argument("--headless")
        # Re-initialize the driver with headless option
        scraper.driver.quit()
        scraper.driver = scraper.driver.__class__(
            service=scraper.driver.service,
            options=scraper.chrome_options
        )
    
    # Run the scraper
    try:
        scraper.scrape_syllabus()
        
        # Download PDFs if requested
        if args.download:
            print("\nDownloading syllabus PDFs...")
            scraper.download_pdfs()
    
    except Exception as e:
        print(f"Error running syllabus scraper: {str(e)}")
    finally:
        # Make sure the driver is closed
        if hasattr(scraper, 'driver') and scraper.driver:
            scraper.driver.quit()

def run_full_website_scraper(args):
    """Run the full website scraper."""
    print("Running Full Website Scraper...\n")
    print(f"Will crawl up to {args.max_pages} pages. This may take a while...\n")
    
    # Create the scraper
    scraper = SRKIWebsiteScraper(output_dir=args.output)
    
    # Set headless mode if requested
    if args.headless:
        scraper.chrome_options.add_argument("--headless")
        # Re-initialize the driver with headless option
        scraper.driver.quit()
        scraper.driver = scraper.driver.__class__(
            service=scraper.driver.service,
            options=scraper.chrome_options
        )
    
    # Run the scraper
    try:
        scraper.crawl_website(max_pages=args.max_pages)
        
        # Download resources if requested
        if args.download:
            print("\nDownloading resources (PDFs and images)...")
            scraper.download_resources(resource_type="all")
    
    except Exception as e:
        print(f"Error running full website scraper: {str(e)}")
    finally:
        # Make sure the driver is closed
        if hasattr(scraper, 'driver') and scraper.driver:
            scraper.driver.quit()

def main():
    """Main function to parse arguments and run the appropriate scraper."""
    print_header()
    
    # Parse command line arguments
    parser = setup_parser()
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    
    # Run the appropriate scraper
    if args.type == 'syllabus':
        run_syllabus_scraper(args)
    elif args.type == 'full':
        run_full_website_scraper(args)
    else:
        print(f"Unknown scraper type: {args.type}")
        parser.print_help()
        return 1
    
    print("\nScraping completed! Results saved to:", args.output)
    return 0

if __name__ == "__main__":
    sys.exit(main()) 