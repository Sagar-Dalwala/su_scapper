# SRKI Website Scraper

This tool provides multiple scrapers for the Shree Ramkrishna Institute website (https://www.srki.ac.in):

1. Syllabus Page Scraper: Extracts syllabus PDF links from the syllabus page
2. Full Website Scraper: Crawls the entire website and extracts all pages, images, and PDFs
3. PDF Downloader: Specialized tool for downloading PDFs that bypasses access restrictions

## Features

### Syllabus Scraper
- Scrapes all syllabus PDF links from undergraduate and postgraduate courses
- Uses multiple scraping strategies to handle dynamic content:
  - Direct extraction from page source
  - Button clicking and table navigation
- Saves results to a CSV file
- Can download all PDFs (optional)
- Handles errors and edge cases

### Full Website Scraper
- Crawls the entire college website
- Extracts all pages, links, images, and PDFs
- Saves HTML content of each page
- Organizes data into CSV and JSON files
- Can download all resources (optional)
- Respects server load with built-in delays
- Special handling for syllabus page

### PDF Downloader
- Specialized tool for downloading PDFs that are protected or have access restrictions
- Uses multiple download methods:
  - Selenium browser automation with keyboard shortcuts
  - Requests with various headers to bypass restrictions
  - Curl as a fallback option
- Can take input from CSV or JSON files
- Handles session validation and referrer checking
- Detailed logging of download attempts

## Requirements

- Python 3.6+
- Chrome browser installed

## Installation

1. Clone this repository:
```
git clone <repository-url>
cd <repository-directory>
```

2. Create a virtual environment and activate it:
```
python -m venv venv
# On Windows
venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate
```

3. Install the required packages:
```
pip install -r requirements.txt
```

## Quick Test

Before running a full scrape, you can verify that the scrapers can access the website and extract data:

```
python test_scraper.py
```

This will run basic tests on both scrapers without creating output files or doing a full crawl.

## Usage

### Quick Start (Recommended)

The easiest way to download all syllabus PDFs is using the `download_syllabus_pdfs.py` script:

```
python download_syllabus_pdfs.py
```

This script will:
1. Run the syllabus scraper to extract all PDF links
2. Run the specialized PDF downloader to download the PDFs

Options:
- `--output`, `-o`: Output directory for data and PDFs [default: output]
- `--skip-scrape`, `-s`: Skip the scraping step and use existing CSV file
- `--input`, `-i`: Input CSV file (only used with --skip-scrape)
- `--headless`: Run browser in headless mode

Examples:
```
# Run with defaults (output to ./output directory)
python download_syllabus_pdfs.py

# Specify output directory
python download_syllabus_pdfs.py --output syllabus_data

# Run in headless mode
python download_syllabus_pdfs.py --headless

# Skip scraping and use existing CSV file
python download_syllabus_pdfs.py --skip-scrape --input output/syllabus_links.csv
```

### Using the Main Script

For more options and full website scraping:

```
python main.py [options]
```

Options:
- `--type`, `-t`: Type of scraper to run (`syllabus` or `full`) [default: syllabus]
- `--output`, `-o`: Output directory for scraped data [default: output]
- `--download`, `-d`: Download resources (PDFs, images) after scraping
- `--max-pages`, `-m`: Maximum number of pages to crawl (for full website scraper) [default: 50]
- `--headless`: Run browser in headless mode (no UI)

Examples:
```
# Run syllabus scraper and download PDFs
python main.py --type syllabus --download

# Run full website scraper with max 100 pages in headless mode
python main.py --type full --max-pages 100 --headless

# Specify a custom output directory
python main.py --output my_data
```

### Using the PDF Downloader Directly

The PDF downloader is specifically designed to handle PDFs that fail to download with the standard methods.

```
python pdf_downloader.py [options]
```

Options:
- `--input`, `-i`: Input CSV or JSON file containing PDF links (from the scraper)
- `--url`: Single PDF URL to download
- `--output`, `-o`: Output directory for downloaded PDFs [default: output]
- `--headless`: Run browser in headless mode

Examples:
```
# Download PDFs from a CSV file
python pdf_downloader.py --input output/syllabus_links.csv

# Download a single PDF
python pdf_downloader.py --url "https://www.srki.ac.in/upload/2021-22/b.sc.%20chemistry%20sem.-ii_1.pdf"

# Download PDFs in headless mode
python pdf_downloader.py --input output/syllabus_links.csv --headless

# Specify output directory
python pdf_downloader.py --input output/syllabus_links.csv --output downloaded_pdfs
```

### Running Individual Scrapers

#### Syllabus Scraper

```
python enhanced_syllabus_scraper.py
```

This will:
1. Visit the syllabus page
2. Extract all PDF links using multiple strategies
3. Save the data to `output/syllabus_links.csv`

#### Full Website Scraper

```
python full_site_scraper.py
```

This will:
1. Crawl the entire website starting from the homepage
2. Special handling for the syllabus page
3. Extract all pages, links, images, and PDFs
4. Save data to CSV and JSON files in the `output` directory

## Output Format

### Syllabus Scraper
The CSV file contains the following columns:
- `course_type`: "Undergraduate" or "Postgraduate"
- `course_name`: Name of the course (e.g., "B.Sc. Computer Science")
- `semester`: Semester information (e.g., "SEMESTER-I")
- `pdf_link`: URL to the syllabus PDF

### Full Website Scraper
The scraper creates multiple output files:
- `pages.csv`: Information about all visited pages
- `pdfs.csv`: All PDF links found on the website
- `images.csv`: All image links found on the website
- `syllabi.csv`: Structured information about syllabus PDFs
- `all_data.json`: All data in JSON format
- `/html/`: Directory containing HTML content of all pages
- `/pdfs/`: Directory for downloaded PDFs (if enabled)
- `/images/`: Directory for downloaded images (if enabled)

## Project Structure

- `enhanced_syllabus_scraper.py`: Syllabus page scraper
- `full_site_scraper.py`: Full website scraper
- `pdf_downloader.py`: Specialized PDF downloader for restricted files
- `download_syllabus_pdfs.py`: Combined script for scraping and downloading syllabus PDFs
- `main.py`: Command-line interface for scrapers
- `test_scraper.py`: Test script to verify functionality
- `requirements.txt`: Required Python packages
- `README.md`: This documentation

## Troubleshooting

- If the regular download methods fail with 403 errors, use the specialized PDF downloader instead
- If the PDF downloader fails, try running it without headless mode to see the browser interactions
- Try adding a referrer header that matches the website (e.g., "https://www.srki.ac.in/pages/su-syllabus/")
- Some PDFs may require browser cookies for access - make sure to let the browser navigate to the site first
- If the scraper fails to find elements, try increasing the wait time in `time.sleep()` calls
- The scraper may need adjustments if the website structure changes 