#!/usr/bin/env python3
"""
SRKI PDF Downloader

This script is specialized for downloading PDFs from the SRKI website.
It uses multiple methods to bypass download restrictions.
"""

import os
import sys
import time
import csv
import json
import argparse
import re
import requests
from urllib.parse import urlparse, urljoin, unquote

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager


class PDFDownloader:
    def __init__(self, output_dir="output", headless=False):
        """Initialize the PDF downloader."""
        self.output_dir = output_dir
        self.headless = headless
        self.pdf_dir = os.path.join(output_dir, "pdfs")
        
        # Create output directories
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if not os.path.exists(self.pdf_dir):
            os.makedirs(self.pdf_dir)
        
        # Initialize driver configuration
        self._setup_driver()
    
    def _setup_driver(self):
        """Set up the Chrome driver with appropriate settings for PDF downloads."""
        # Configure Chrome options
        self.chrome_options = Options()
        
        if self.headless:
            self.chrome_options.add_argument("--headless")
        
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--disable-notifications")
        
        # Set up download preferences
        download_prefs = {
            "download.default_directory": os.path.abspath(self.pdf_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,  # Don't open PDFs in browser
            "profile.default_content_settings.popups": 0,
        }
        self.chrome_options.add_experimental_option("prefs", download_prefs)
        
        # Initialize WebDriver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.chrome_options
        )
        
        # Set implicit wait
        self.driver.implicitly_wait(5)
    
    def load_pdf_links(self, input_file):
        """Load PDF links from a CSV or JSON file."""
        pdf_links = []
        file_ext = os.path.splitext(input_file)[1].lower()
        
        try:
            if file_ext == '.csv':
                with open(input_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'pdf_link' in row:
                            pdf_links.append({
                                'url': row['pdf_link'],
                                'course_name': row.get('course_name', 'Unknown'),
                                'semester': row.get('semester', 'Unknown')
                            })
                        elif 'url' in row and row['url'].endswith('.pdf'):
                            pdf_links.append({
                                'url': row['url'],
                                'text': row.get('text', 'Unknown')
                            })
            
            elif file_ext == '.json':
                with open(input_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Handle different JSON structures
                    if isinstance(data, list):
                        for item in data:
                            if 'pdf_link' in item:
                                pdf_links.append({
                                    'url': item['pdf_link'],
                                    'course_name': item.get('course_name', 'Unknown'),
                                    'semester': item.get('semester', 'Unknown')
                                })
                            elif 'url' in item and item['url'].endswith('.pdf'):
                                pdf_links.append({
                                    'url': item['url'],
                                    'text': item.get('text', 'Unknown')
                                })
                    
                    elif isinstance(data, dict):
                        # Try to find arrays of PDFs within the structure
                        if 'pdfs' in data and isinstance(data['pdfs'], list):
                            for item in data['pdfs']:
                                if 'url' in item and item['url'].endswith('.pdf'):
                                    pdf_links.append(item)
                        
                        if 'syllabi' in data and isinstance(data['syllabi'], list):
                            for item in data['syllabi']:
                                if 'pdf_link' in item:
                                    pdf_links.append({
                                        'url': item['pdf_link'],
                                        'course_name': item.get('course_name', 'Unknown'),
                                        'semester': item.get('semester', 'Unknown')
                                    })
            
            else:
                print(f"Unsupported file format: {file_ext}")
                return []
            
            return pdf_links
        
        except Exception as e:
            print(f"Error loading PDF links from {input_file}: {str(e)}")
            return []
    
    def _get_filename_from_url(self, url, metadata=None):
        """Generate a filename from the URL and metadata."""
        # Extract the filename from the URL
        filename = unquote(os.path.basename(urlparse(url).path))
        
        # Remove any query parameters
        filename = filename.split('?')[0]
        
        # If we have metadata, create a more descriptive filename
        if metadata:
            if 'course_name' in metadata and 'semester' in metadata:
                course_name = metadata['course_name'].replace(" ", "_").replace(".", "")
                semester = metadata['semester'].replace(" ", "_").replace("-", "_")
                new_filename = f"{course_name}_{semester}.pdf"
                return new_filename
            elif 'text' in metadata:
                # Create a filename from the text description
                text = re.sub(r'[\\/*?:"<>|]', "_", metadata['text'])
                text = text.replace(" ", "_")[:50]  # Limit length
                return f"{text}.pdf"
        
        return filename
    
    def _download_pdf_with_selenium(self, url, filepath):
        """Try to download a PDF using Selenium with various methods."""
        try:
            print(f"Attempting to download with Selenium: {url}")
            
            # Navigate to the PDF URL
            self.driver.get(url)
            time.sleep(3)  # Wait for the page to load
            
            # Method 1: Check if it's loaded in an iframe
            try:
                iframe = self.driver.find_element(By.TAG_NAME, "iframe")
                iframe_src = iframe.get_attribute("src")
                if iframe_src and iframe_src.endswith('.pdf'):
                    print("  Found PDF in iframe, navigating to it...")
                    self.driver.get(iframe_src)
                    time.sleep(2)
            except NoSuchElementException:
                pass  # No iframe found, continue with current page
            
            # Method 2: Try to use keyboard shortcut to save
            try:
                actions = ActionChains(self.driver)
                actions.key_down(Keys.CONTROL).send_keys('s').key_up(Keys.CONTROL).perform()
                time.sleep(2)  # Wait for save dialog
                actions.send_keys(Keys.ENTER).perform()
                time.sleep(2)  # Wait for save to complete
                print("  Used keyboard shortcut method")
                return True
            except Exception as e:
                print(f"  Keyboard shortcut method failed: {str(e)}")
            
            # Method 3: Try to extract PDF content directly
            try:
                pdf_content = self.driver.execute_script("return document.body.innerHTML")
                if pdf_content and "%PDF-" in pdf_content:
                    print("  Found raw PDF content, saving directly...")
                    with open(filepath, 'wb') as f:
                        f.write(pdf_content.encode('utf-8'))
                    return True
            except Exception as e:
                print(f"  Direct content extraction failed: {str(e)}")
            
            # Method 4: Try to find a download button
            try:
                download_buttons = self.driver.find_elements(By.XPATH, 
                    "//a[contains(@href, 'download') or contains(@id, 'download') or contains(@class, 'download')]")
                
                if download_buttons:
                    for button in download_buttons:
                        try:
                            button.click()
                            time.sleep(3)  # Wait for download to start
                            print("  Clicked download button")
                            return True
                        except:
                            continue
            except Exception as e:
                print(f"  Download button method failed: {str(e)}")
            
            return False
        
        except Exception as e:
            print(f"  Selenium download failed: {str(e)}")
            return False
    
    def _download_pdf_with_requests(self, url, filepath):
        """Try to download a PDF using requests with various headers."""
        try:
            print(f"Attempting to download with requests: {url}")
            
            # Try different headers to bypass restrictions
            headers_list = [
                {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                },
                {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
                    'Referer': 'https://www.srki.ac.in/'
                },
                {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Referer': 'https://www.srki.ac.in/pages/su-syllabus/'
                }
            ]
            
            for headers in headers_list:
                try:
                    response = requests.get(url, headers=headers, stream=True, timeout=10)
                    if response.status_code == 200:
                        # Check if it's actually a PDF
                        content_type = response.headers.get('Content-Type', '').lower()
                        if 'application/pdf' in content_type or response.content.startswith(b'%PDF'):
                            with open(filepath, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            print(f"  Success with headers: {headers['User-Agent'][:20]}...")
                            return True
                        else:
                            print(f"  Response was not a PDF (Content-Type: {content_type})")
                    else:
                        print(f"  Failed with status code: {response.status_code} using headers: {headers['User-Agent'][:20]}...")
                except Exception as e:
                    print(f"  Request failed with headers {headers['User-Agent'][:20]}...: {str(e)}")
            
            return False
            
        except Exception as e:
            print(f"  Requests download failed: {str(e)}")
            return False
    
    def _download_pdf_with_curl(self, url, filepath):
        """Try to download a PDF using curl command."""
        try:
            print(f"Attempting to download with curl: {url}")
            
            # Use curl with various user agents and referer headers
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            referer = "https://www.srki.ac.in/pages/su-syllabus/"
            
            import subprocess
            cmd = [
                "curl", "-L", "-o", filepath,
                "-A", user_agent,
                "-e", referer,
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                print("  Downloaded successfully with curl")
                
                # Verify it's actually a PDF
                with open(filepath, 'rb') as f:
                    header = f.read(5)
                    if header == b'%PDF-':
                        return True
                    else:
                        print("  Downloaded file is not a valid PDF")
                        return False
            else:
                print(f"  Curl failed with return code {result.returncode}")
                if result.stderr:
                    print(f"  Error: {result.stderr}")
                return False
            
        except Exception as e:
            print(f"  Curl download failed: {str(e)}")
            return False
    
    def download_pdf(self, url, metadata=None):
        """Try multiple methods to download a PDF."""
        try:
            # Create a filename based on the URL and metadata
            filename = self._get_filename_from_url(url, metadata)
            filepath = os.path.join(self.pdf_dir, filename)
            
            print(f"\nDownloading PDF: {filename}")
            print(f"URL: {url}")
            
            # First, check if we need to bypass caching
            url_with_nocache = url
            if "?" not in url:
                url_with_nocache = f"{url}?nocache={int(time.time())}"
            
            # Try Selenium method
            if self._download_pdf_with_selenium(url_with_nocache, filepath):
                return True
            
            # Try requests method
            if self._download_pdf_with_requests(url_with_nocache, filepath):
                return True
            
            # Try curl as a last resort
            if self._download_pdf_with_curl(url_with_nocache, filepath):
                return True
            
            print("All download methods failed")
            return False
            
        except Exception as e:
            print(f"Error downloading PDF: {str(e)}")
            return False
    
    def download_pdfs_from_file(self, input_file):
        """Download PDFs from a file containing links."""
        pdf_links = self.load_pdf_links(input_file)
        
        if not pdf_links:
            print(f"No PDF links found in {input_file}")
            return
        
        print(f"Found {len(pdf_links)} PDF links in {input_file}")
        
        success_count = 0
        for i, pdf_info in enumerate(pdf_links):
            print(f"\nProcessing PDF {i+1}/{len(pdf_links)}")
            
            url = pdf_info['url']
            if self.download_pdf(url, pdf_info):
                success_count += 1
            
            # Add a small delay between downloads to not overwhelm the server
            time.sleep(1)
        
        print(f"\nDownloaded {success_count} out of {len(pdf_links)} PDFs successfully")
    
    def download_pdfs_from_list(self, urls):
        """Download PDFs from a list of URLs."""
        if not urls:
            print("No URLs provided")
            return
        
        success_count = 0
        for i, url in enumerate(urls):
            print(f"\nProcessing PDF {i+1}/{len(urls)}")
            
            if self.download_pdf(url):
                success_count += 1
            
            # Add a small delay between downloads to not overwhelm the server
            time.sleep(1)
        
        print(f"\nDownloaded {success_count} out of {len(urls)} PDFs successfully")
    
    def cleanup(self):
        """Close the browser and clean up."""
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()


def main():
    """Main function for the PDF downloader."""
    parser = argparse.ArgumentParser(description='Download PDFs from SRKI website.')
    
    # Add arguments
    parser.add_argument('--input', '-i', 
                        help='Input CSV or JSON file containing PDF links')
    
    parser.add_argument('--url', 
                        help='Single PDF URL to download')
    
    parser.add_argument('--output', '-o', default='output',
                        help='Output directory for downloaded PDFs')
    
    parser.add_argument('--headless', action='store_true',
                        help='Run browser in headless mode')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate arguments
    if not args.input and not args.url:
        parser.print_help()
        print("\nError: Either --input or --url must be provided")
        return 1
    
    try:
        # Create downloader
        downloader = PDFDownloader(output_dir=args.output, headless=args.headless)
        
        # Process based on input type
        if args.input:
            downloader.download_pdfs_from_file(args.input)
        elif args.url:
            downloader.download_pdf(args.url)
        
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    finally:
        # Clean up
        if 'downloader' in locals():
            downloader.cleanup()


if __name__ == "__main__":
    sys.exit(main()) 