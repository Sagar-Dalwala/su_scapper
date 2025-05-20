import time
import csv
import os
import re
import json
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup
import requests


class SRKIWebsiteScraper:
    def __init__(self, output_dir="output", base_url="https://www.srki.ac.in"):
        """Initialize the website scraper."""
        self.base_url = base_url
        self.output_dir = output_dir
        self.visited_urls = set()
        self.queue = []
        self.data = {
            "pages": [],
            "pdfs": [],
            "images": [],
            "syllabi": []
        }
        
        # Create output directories
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Create subdirectories
        for dir_name in ["pdfs", "images", "html"]:
            dir_path = os.path.join(output_dir, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        
        # Configure Chrome options
        self.chrome_options = Options()
        # Uncomment below line to run in headless mode (without browser UI)
        # self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--disable-notifications")
        
        # Initialize WebDriver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.chrome_options
        )
        
        # Set implicit wait
        self.driver.implicitly_wait(5)
    
    def is_valid_url(self, url):
        """Check if a URL is valid for scraping."""
        # Parse the URL
        parsed_url = urlparse(url)
        
        # Check if the URL belongs to the base domain
        if self.base_url.split("//")[1] not in parsed_url.netloc:
            return False
        
        # Skip URLs with certain extensions to avoid unnecessary navigation
        skip_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
        if any(parsed_url.path.endswith(ext) for ext in skip_extensions):
            return False
        
        # Skip URLs that have been visited
        if url in self.visited_urls:
            return False
        
        return True
    
    def extract_links_from_page(self, url):
        """Extract all links from a page."""
        links = []
        
        try:
            # Wait for the page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extract links from the page
            elements = self.driver.find_elements(By.TAG_NAME, "a")
            
            for element in elements:
                try:
                    href = element.get_attribute("href")
                    if href and href.startswith("http"):
                        links.append(href)
                except StaleElementReferenceException:
                    continue
            
            return links
        except Exception as e:
            print(f"Error extracting links from {url}: {str(e)}")
            return []
    
    def extract_resources(self, url):
        """Extract resources like images and PDFs from the page."""
        resources = {
            "images": [],
            "pdfs": []
        }
        
        try:
            # Extract images
            img_elements = self.driver.find_elements(By.TAG_NAME, "img")
            for img in img_elements:
                try:
                    src = img.get_attribute("src")
                    if src and src.startswith("http"):
                        resources["images"].append({
                            "url": src,
                            "alt": img.get_attribute("alt") or "",
                            "source_page": url
                        })
                except StaleElementReferenceException:
                    continue
            
            # Extract PDFs
            pdf_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
            for pdf in pdf_links:
                try:
                    href = pdf.get_attribute("href")
                    if href and href.endswith(".pdf"):
                        resources["pdfs"].append({
                            "url": href,
                            "text": pdf.text.strip() or "Unnamed PDF",
                            "source_page": url
                        })
                except StaleElementReferenceException:
                    continue
            
            return resources
        except Exception as e:
            print(f"Error extracting resources from {url}: {str(e)}")
            return resources
    
    def extract_page_content(self, url):
        """Extract and save the content of a page."""
        try:
            # Get the page source
            page_source = self.driver.page_source
            page_title = self.driver.title
            
            # Create a BeautifulSoup object for better content extraction
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract main content (this will vary based on the site structure)
            main_content = ""
            content_div = soup.select_one("div.container") or soup.select_one("main") or soup.select_one("article")
            if content_div:
                main_content = content_div.get_text(separator=' ', strip=True)
            
            # Create a page entry
            page_data = {
                "url": url,
                "title": page_title,
                "content": main_content[:1000] + "..." if len(main_content) > 1000 else main_content,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save the HTML file
            filename = url.replace(self.base_url, "").replace("/", "_").replace("?", "_")
            if not filename:
                filename = "index"
            if not filename.endswith(".html"):
                filename += ".html"
            
            # Make sure filename is valid
            filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
            
            # Save the HTML file
            html_path = os.path.join(self.output_dir, "html", filename)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(page_source)
            
            page_data["saved_file"] = html_path
            
            return page_data
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return {
                "url": url,
                "title": "Error page",
                "content": f"Error: {str(e)}",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def crawl_syllabus_page(self):
        """Special handler for the syllabus page to extract PDF links."""
        url = urljoin(self.base_url, "/pages/su-syllabus/")
        
        try:
            print(f"Crawling syllabus page: {url}")
            self.driver.get(url)
            time.sleep(3)  # Wait for page to load
            
            # Extract PDF links from the page source
            page_source = self.driver.page_source
            
            # Use a regex pattern to find all PDF links
            pdf_pattern = r'href="(https://www\.srki\.ac\.in/upload/[^"]+\.pdf)"'
            pdf_links = re.findall(pdf_pattern, page_source)
            
            # Extract information about each PDF
            for link in pdf_links:
                try:
                    # Extract filename from URL
                    filename = link.split('/')[-1]
                    
                    # Try to determine course type, name, and semester
                    course_type = "Unknown"
                    course_name = "Unknown"
                    semester = "Unknown"
                    
                    # Pattern matching for different course types
                    if "bsc" in filename.lower() or "b.sc" in filename.lower():
                        course_type = "Undergraduate"
                        
                        # Extract course name
                        if "cs" in filename.lower():
                            course_name = "B.Sc. Computer Science"
                        elif "it" in filename.lower():
                            course_name = "B.Sc. Information Technology"
                        elif "bt" in filename.lower() or "bio" in filename.lower():
                            course_name = "B.Sc. Biotechnology"
                        elif "ch" in filename.lower():
                            course_name = "B.Sc. Chemistry"
                        elif "mb" in filename.lower() or "micro" in filename.lower():
                            course_name = "B.Sc. Microbiology"
                        elif "en" in filename.lower() or "env" in filename.lower():
                            course_name = "B.Sc. Environmental Science"
                    
                    elif "msc" in filename.lower() or "m.sc" in filename.lower():
                        course_type = "Postgraduate"
                        
                        # Extract course name
                        if "cs" in filename.lower():
                            course_name = "M.Sc. Computer Science"
                        elif "it" in filename.lower():
                            course_name = "M.Sc. Information Technology"
                        elif "ac" in filename.lower():
                            course_name = "M.Sc. Advance Computing"
                        elif "wmt" in filename.lower():
                            course_name = "M.Sc. Web and Mobile Technology"
                        elif "bt" in filename.lower() or "bio" in filename.lower():
                            course_name = "M.Sc. Biotechnology"
                        elif "medical bt" in filename.lower():
                            course_name = "M.Sc. Medical Biotechnology"
                        elif "mb" in filename.lower() or "micro" in filename.lower():
                            course_name = "M.Sc. Microbiology"
                        elif "gen" in filename.lower():
                            course_name = "M.Sc. Genetics"
                        elif "clin" in filename.lower() or "embryo" in filename.lower():
                            course_name = "M.Sc. Clinical Embryology"
                    
                    elif "pgdmlt" in filename.lower():
                        course_type = "Postgraduate"
                        course_name = "PGDMLT"
                    
                    # Extract semester information
                    sem_match = re.search(r'sem[- ]*([1-6i]|iv|v|vi)', filename.lower())
                    if sem_match:
                        sem_number = sem_match.group(1)
                        semester = f"SEMESTER-{sem_number.upper()}"
                    
                    # Add to syllabus data
                    self.data["syllabi"].append({
                        "course_type": course_type,
                        "course_name": course_name,
                        "semester": semester,
                        "pdf_link": link,
                        "filename": filename
                    })
                
                except Exception as e:
                    print(f"Error processing syllabus PDF link {link}: {str(e)}")
            
            print(f"Found {len(self.data['syllabi'])} syllabus PDF links")
            
            # Also add to general PDFs list
            for syllabus in self.data["syllabi"]:
                self.data["pdfs"].append({
                    "url": syllabus["pdf_link"],
                    "text": f"{syllabus['course_name']} - {syllabus['semester']}",
                    "source_page": url
                })
            
            return True
            
        except Exception as e:
            print(f"Error crawling syllabus page: {str(e)}")
            return False
    
    def crawl_website(self, max_pages=100):
        """Crawl the website starting from the homepage."""
        try:
            # Start with the homepage
            start_url = self.base_url
            self.queue.append(start_url)
            
            # First, crawl the syllabus page specifically
            self.crawl_syllabus_page()
            
            # Then do general crawling
            page_count = 0
            
            while self.queue and page_count < max_pages:
                # Get the next URL from the queue
                current_url = self.queue.pop(0)
                
                # Skip if already visited
                if current_url in self.visited_urls:
                    continue
                
                print(f"Crawling ({page_count + 1}/{max_pages}): {current_url}")
                
                try:
                    # Visit the page
                    self.driver.get(current_url)
                    
                    # Mark as visited
                    self.visited_urls.add(current_url)
                    page_count += 1
                    
                    # Extract links
                    links = self.extract_links_from_page(current_url)
                    
                    # Extract resources
                    resources = self.extract_resources(current_url)
                    self.data["images"].extend(resources["images"])
                    self.data["pdfs"].extend(resources["pdfs"])
                    
                    # Extract page content
                    page_data = self.extract_page_content(current_url)
                    self.data["pages"].append(page_data)
                    
                    # Add valid links to the queue
                    for link in links:
                        if self.is_valid_url(link) and link not in self.queue:
                            self.queue.append(link)
                    
                    # Save intermediate results every 10 pages
                    if page_count % 10 == 0:
                        self.save_results()
                    
                    # Small delay to be respectful to the server
                    time.sleep(1)
                
                except Exception as e:
                    print(f"Error processing {current_url}: {str(e)}")
            
            # Save final results
            self.save_results()
            
            print(f"Crawling completed. Visited {len(self.visited_urls)} pages.")
            
        except Exception as e:
            print(f"Error during crawling: {str(e)}")
        finally:
            # Clean up
            self.driver.quit()
    
    def save_results(self):
        """Save the scraped data to various files."""
        try:
            # Save pages data
            with open(os.path.join(self.output_dir, "pages.csv"), "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["url", "title", "content", "timestamp", "saved_file"])
                writer.writeheader()
                for page in self.data["pages"]:
                    writer.writerow(page)
            
            # Save PDFs data
            with open(os.path.join(self.output_dir, "pdfs.csv"), "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["url", "text", "source_page"])
                writer.writeheader()
                for pdf in self.data["pdfs"]:
                    writer.writerow(pdf)
            
            # Save images data
            with open(os.path.join(self.output_dir, "images.csv"), "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["url", "alt", "source_page"])
                writer.writeheader()
                for image in self.data["images"]:
                    writer.writerow(image)
            
            # Save syllabi data
            with open(os.path.join(self.output_dir, "syllabi.csv"), "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["course_type", "course_name", "semester", "pdf_link", "filename"])
                writer.writeheader()
                for syllabus in self.data["syllabi"]:
                    writer.writerow(syllabus)
            
            # Save all data as JSON
            with open(os.path.join(self.output_dir, "all_data.json"), "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
            
            print(f"Data saved successfully. {len(self.data['pages'])} pages, {len(self.data['pdfs'])} PDFs, {len(self.data['images'])} images, {len(self.data['syllabi'])} syllabi.")
            
        except Exception as e:
            print(f"Error saving results: {str(e)}")
    
    def download_resources(self, resource_type="all"):
        """Download resources (PDFs, images) from the scraped data."""
        try:
            # Download PDFs
            if resource_type in ["all", "pdf", "pdfs"]:
                pdf_dir = os.path.join(self.output_dir, "pdfs")
                if not os.path.exists(pdf_dir):
                    os.makedirs(pdf_dir)
                
                downloaded_pdfs = 0
                
                # Create a set of unique PDF URLs to avoid duplicates
                unique_pdfs = set()
                for pdf in self.data["pdfs"]:
                    unique_pdfs.add(pdf["url"])
                
                # Configure Chrome options for PDF downloading
                download_options = Options()
                download_options.add_argument("--window-size=1920,1080")
                download_options.add_argument("--disable-notifications")
                
                # Set up download preferences
                download_prefs = {
                    "download.default_directory": os.path.abspath(pdf_dir),
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "plugins.always_open_pdf_externally": True,  # Don't open PDFs in browser
                }
                download_options.add_experimental_option("prefs", download_prefs)
                
                # Create a separate driver just for downloading
                download_driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=download_options
                )
                
                # If headless was enabled in original driver, enable it here too
                if "--headless" in self.chrome_options.arguments:
                    download_options.add_argument("--headless")
                    download_driver.quit()
                    download_driver = webdriver.Chrome(
                        service=Service(ChromeDriverManager().install()),
                        options=download_options
                    )
                
                try:
                    for i, pdf_url in enumerate(unique_pdfs):
                        try:
                            # Create a safe filename
                            filename = pdf_url.split("/")[-1]
                            filepath = os.path.join(pdf_dir, filename)
                            
                            print(f"Downloading PDF ({i+1}/{len(unique_pdfs)}): {filename}")
                            
                            # Use Selenium to navigate to the PDF page
                            download_driver.get(pdf_url)
                            time.sleep(3)  # Wait for the PDF to load
                            
                            # Some sites may render the PDF in an iframe or object tag
                            try:
                                # Try to find a PDF viewer iframe
                                iframe = download_driver.find_element(By.TAG_NAME, "iframe")
                                pdf_src = iframe.get_attribute("src")
                                if pdf_src:
                                    download_driver.get(pdf_src)
                                    time.sleep(2)
                            except Exception:
                                # Iframe not found, continue with current page
                                pass
                            
                            # Save PDF content using browser's save dialog keyboard shortcut
                            try:
                                # Try to use keyboard shortcut to save (Ctrl+S)
                                actions = ActionChains(download_driver)
                                actions.key_down(Keys.CONTROL).send_keys('s').key_up(Keys.CONTROL).perform()
                                time.sleep(2)  # Wait for save dialog
                                
                                # Press Enter to confirm save
                                actions.send_keys(Keys.ENTER).perform()
                                time.sleep(2)  # Wait for save to complete
                                
                                downloaded_pdfs += 1
                                print(f"Successfully saved: {filename}")
                            except Exception as e:
                                print(f"Error saving PDF with keyboard shortcut: {str(e)}")
                                
                                # Alternative approach: Try to get the PDF content directly
                                try:
                                    # Get the PDF content
                                    pdf_content = download_driver.execute_script("return document.body.outerHTML")
                                    
                                    # If this isn't a PDF viewer page but the actual PDF, write it to file
                                    if pdf_content and "<html" not in pdf_content.lower():
                                        with open(filepath, 'wb') as f:
                                            f.write(pdf_content.encode('utf-8'))
                                        downloaded_pdfs += 1
                                        print(f"Successfully saved PDF content: {filename}")
                                    else:
                                        # Try traditional requests approach as a fallback
                                        response = requests.get(pdf_url, stream=True)
                                        if response.status_code == 200:
                                            with open(filepath, 'wb') as f:
                                                for chunk in response.iter_content(chunk_size=8192):
                                                    f.write(chunk)
                                            downloaded_pdfs += 1
                                            print(f"Downloaded via requests: {filename}")
                                        else:
                                            print(f"Failed to download {pdf_url}, status code: {response.status_code}")
                                except Exception as inner_e:
                                    print(f"Error extracting PDF content: {str(inner_e)}")
                        
                        except Exception as e:
                            print(f"Error downloading PDF {pdf_url}: {str(e)}")
                    
                    print(f"Downloaded {downloaded_pdfs} PDFs")
                
                finally:
                    # Clean up
                    if download_driver:
                        download_driver.quit()
            
            # Download images (keep using the requests method since it works for images)
            if resource_type in ["all", "image", "images"]:
                img_dir = os.path.join(self.output_dir, "images")
                downloaded_images = 0
                
                # Create a set of unique image URLs to avoid duplicates
                unique_images = set()
                for img in self.data["images"]:
                    unique_images.add(img["url"])
                
                for img_url in unique_images:
                    try:
                        # Create a safe filename
                        filename = img_url.split("/")[-1]
                        
                        # Add an extension if missing
                        if "." not in filename:
                            filename += ".jpg"
                        
                        filepath = os.path.join(img_dir, filename)
                        
                        # Download the image
                        response = requests.get(img_url, stream=True)
                        if response.status_code == 200:
                            with open(filepath, "wb") as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            downloaded_images += 1
                            print(f"Downloaded image ({downloaded_images}/{len(unique_images)}): {filename}")
                        else:
                            print(f"Failed to download image {img_url}, status code: {response.status_code}")
                    
                    except Exception as e:
                        print(f"Error downloading image {img_url}: {str(e)}")
                
                print(f"Downloaded {downloaded_images} images")
            
        except Exception as e:
            print(f"Error downloading resources: {str(e)}")


if __name__ == "__main__":
    # Create and run the scraper
    scraper = SRKIWebsiteScraper()
    
    # Set max_pages to control how many pages to crawl (adjust as needed)
    max_pages = 50
    
    # Start crawling
    scraper.crawl_website(max_pages=max_pages)
    
    # Download resources
    # Uncomment to download resources
    # scraper.download_resources(resource_type="all") 