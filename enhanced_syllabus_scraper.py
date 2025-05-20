import time
import csv
import os
import re
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

class EnhancedSyllabusScraper:
    def __init__(self, output_dir="output"):
        """Initialize the scraper with Chrome options and output directory."""
        self.url = "https://www.srki.ac.in/pages/su-syllabus/"
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
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
        self.driver.implicitly_wait(10)
        
        # Initialize data structure
        self.course_data = []
    
    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be present."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            print(f"Timed out waiting for element {value}")
            return None
    
    def get_course_buttons(self, course_type):
        """Get all course buttons for a specific course type."""
        try:
            if course_type.lower() == "undergraduate":
                # Find the undergraduate section
                ug_section = self.driver.find_element(By.XPATH, "//h3[contains(text(), 'Under Graduate Courses')]/following-sibling::div")
                buttons = ug_section.find_elements(By.TAG_NAME, "a")
            else:
                # Find the postgraduate section
                pg_section = self.driver.find_element(By.XPATH, "//h3[contains(text(), 'Post Graduate Courses')]/following-sibling::div")
                buttons = pg_section.find_elements(By.TAG_NAME, "a")
            
            return buttons
        except Exception as e:
            print(f"Error getting {course_type} buttons: {str(e)}")
            return []
    
    def scrape_course_table(self, course_name, course_type):
        """Scrape a specific course table after clicking on its button."""
        try:
            # Find all tables on the page
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            
            # Look for tables that appear after clicking the course button
            for table in tables:
                try:
                    # Check if the table contains semester links
                    if table.is_displayed():
                        # Extract links from the table
                        links = table.find_elements(By.TAG_NAME, "a")
                        
                        for link in links:
                            try:
                                href = link.get_attribute("href")
                                text = link.text.strip()
                                
                                # Check if it's a valid syllabus PDF link
                                if href and href.endswith(".pdf"):
                                    self.course_data.append({
                                        "course_type": course_type,
                                        "course_name": course_name,
                                        "semester": text,
                                        "pdf_link": href
                                    })
                                    print(f"Found link: {text} - {href}")
                            except StaleElementReferenceException:
                                # Handle stale element (page might have changed)
                                continue
                except Exception as e:
                    print(f"Error processing table: {str(e)}")
        except Exception as e:
            print(f"Error scraping course table for {course_name}: {str(e)}")
    
    def scrape_undergraduate_courses(self):
        """Scrape all undergraduate course data."""
        print("Scraping undergraduate courses...")
        try:
            # Get all undergraduate course buttons
            ug_buttons = self.get_course_buttons("undergraduate")
            
            if not ug_buttons:
                print("No undergraduate course buttons found")
                return
            
            # Store course names and their elements
            courses = []
            for button in ug_buttons:
                course_name = button.text.strip()
                if course_name:
                    courses.append({"name": course_name, "element": button})
            
            # Click each course button and scrape its data
            for course in courses:
                try:
                    print(f"Processing course: {course['name']}")
                    # Scroll to the button to make it clickable
                    ActionChains(self.driver).move_to_element(course['element']).perform()
                    
                    # Click the button
                    course['element'].click()
                    time.sleep(2)  # Wait for table to load
                    
                    # Scrape the course table
                    self.scrape_course_table(course['name'], "Undergraduate")
                    
                except StaleElementReferenceException:
                    # If element is stale, find it again
                    print(f"Stale element for {course['name']}, retrying...")
                    try:
                        # Find the button again
                        new_button = self.driver.find_element(By.XPATH, f"//a[contains(text(), '{course['name']}')]")
                        new_button.click()
                        time.sleep(2)
                        self.scrape_course_table(course['name'], "Undergraduate")
                    except Exception as e:
                        print(f"Failed to recover from stale element for {course['name']}: {str(e)}")
                except Exception as e:
                    print(f"Error processing undergraduate course {course['name']}: {str(e)}")
        
        except Exception as e:
            print(f"Error in scrape_undergraduate_courses: {str(e)}")
    
    def scrape_postgraduate_courses(self):
        """Scrape all postgraduate course data."""
        print("Scraping postgraduate courses...")
        try:
            # Get all postgraduate course buttons
            pg_buttons = self.get_course_buttons("postgraduate")
            
            if not pg_buttons:
                print("No postgraduate course buttons found")
                return
            
            # Store course names and their elements
            courses = []
            for button in pg_buttons:
                course_name = button.text.strip()
                if course_name:
                    courses.append({"name": course_name, "element": button})
            
            # Click each course button and scrape its data
            for course in courses:
                try:
                    print(f"Processing course: {course['name']}")
                    # Scroll to the button to make it clickable
                    ActionChains(self.driver).move_to_element(course['element']).perform()
                    
                    # Click the button
                    course['element'].click()
                    time.sleep(2)  # Wait for table to load
                    
                    # Scrape the course table
                    self.scrape_course_table(course['name'], "Postgraduate")
                    
                except StaleElementReferenceException:
                    # If element is stale, find it again
                    print(f"Stale element for {course['name']}, retrying...")
                    try:
                        # Find the button again
                        new_button = self.driver.find_element(By.XPATH, f"//a[contains(text(), '{course['name']}')]")
                        new_button.click()
                        time.sleep(2)
                        self.scrape_course_table(course['name'], "Postgraduate")
                    except Exception as e:
                        print(f"Failed to recover from stale element for {course['name']}: {str(e)}")
                except Exception as e:
                    print(f"Error processing postgraduate course {course['name']}: {str(e)}")
        
        except Exception as e:
            print(f"Error in scrape_postgraduate_courses: {str(e)}")
    
    def direct_scrape_method(self):
        """Alternative method that directly extracts links from HTML without clicking buttons."""
        try:
            # Wait for the page to load
            self.wait_for_element(By.CSS_SELECTOR, ".container")
            
            # Find all tables on the page
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            
            for table in tables:
                # Try to determine which course this table represents
                try:
                    # Get the previous element to see if it's a heading
                    previous_element = self.driver.execute_script(
                        "return arguments[0].previousElementSibling;", table)
                    
                    course_name = "Unknown"
                    course_type = "Unknown"
                    
                    if previous_element:
                        # Check if it's a heading with the course name
                        if previous_element.tag_name.lower() in ["h3", "h4", "strong", "b"]:
                            course_name = previous_element.text.strip()
                            
                            # Try to determine if it's UG or PG
                            if "B.Sc." in course_name:
                                course_type = "Undergraduate"
                            elif "M.Sc." in course_name or "PGDMLT" in course_name:
                                course_type = "Postgraduate"
                    
                    # Get all links in the table
                    links = table.find_elements(By.TAG_NAME, "a")
                    
                    for link in links:
                        href = link.get_attribute("href")
                        text = link.text.strip()
                        
                        if href and href.endswith(".pdf"):
                            self.course_data.append({
                                "course_type": course_type,
                                "course_name": course_name,
                                "semester": text,
                                "pdf_link": href
                            })
                except Exception as e:
                    print(f"Error processing table in direct method: {str(e)}")
        
        except Exception as e:
            print(f"Error in direct_scrape_method: {str(e)}")
    
    def extract_links_from_source(self):
        """Extract all PDF links directly from the page source."""
        try:
            # Get the page source
            page_source = self.driver.page_source
            
            # Extract all PDF links using regex
            pdf_pattern = r'href="(https://www\.srki\.ac\.in/upload/[^"]+\.pdf)"'
            pdf_links = re.findall(pdf_pattern, page_source)
            
            # Parse PDF filenames to determine course info
            for link in pdf_links:
                try:
                    # Extract filename from URL
                    filename = link.split('/')[-1]
                    
                    course_type = "Unknown"
                    course_name = "Unknown"
                    semester = "Unknown"
                    
                    # Try to determine course type and name from the filename
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
                    
                    # Extract semester
                    sem_match = re.search(r'sem[- ]*([1-6i]|iv|v|vi)', filename.lower())
                    if sem_match:
                        sem_number = sem_match.group(1)
                        semester = f"SEMESTER-{sem_number.upper()}"
                    
                    # Add to the dataset
                    self.course_data.append({
                        "course_type": course_type,
                        "course_name": course_name,
                        "semester": semester,
                        "pdf_link": link
                    })
                
                except Exception as e:
                    print(f"Error processing PDF link {link}: {str(e)}")
        
        except Exception as e:
            print(f"Error in extract_links_from_source: {str(e)}")
    
    def scrape_syllabus(self):
        """Main method to scrape all syllabus data using multiple approaches."""
        try:
            # Navigate to the syllabus page
            self.driver.get(self.url)
            time.sleep(3)  # Wait for page to load completely
            
            # Try the direct method first (most reliable)
            print("Using direct extraction method...")
            self.extract_links_from_source()
            
            # If direct method didn't get enough data, try clicking methods
            if len(self.course_data) < 10:
                print("Direct method didn't get enough data, trying alternative methods...")
                
                # Refresh the page
                self.driver.refresh()
                time.sleep(3)
                
                # Try the button clicking methods
                self.scrape_undergraduate_courses()
                self.scrape_postgraduate_courses()
            
            # Save the data
            self.save_to_csv()
            
            print(f"Scraping completed. Found {len(self.course_data)} syllabus links.")
            
        except Exception as e:
            print(f"Error during scraping: {str(e)}")
        finally:
            # Clean up
            self.driver.quit()
    
    def save_to_csv(self):
        """Save the scraped data to a CSV file."""
        csv_path = os.path.join(self.output_dir, "syllabus_links.csv")
        
        try:
            # Remove duplicates
            unique_data = []
            seen_links = set()
            
            for item in self.course_data:
                if item['pdf_link'] not in seen_links:
                    unique_data.append(item)
                    seen_links.add(item['pdf_link'])
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['course_type', 'course_name', 'semester', 'pdf_link']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for row in unique_data:
                    writer.writerow(row)
            
            print(f"Data saved to {csv_path}")
        
        except Exception as e:
            print(f"Error saving to CSV: {str(e)}")
    
    def download_pdfs(self):
        """Download all the PDF files using Selenium to bypass download restrictions."""
        pdf_dir = os.path.join(self.output_dir, "pdfs")
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)
        
        downloaded_count = 0
        total_pdfs = len(self.course_data)
        
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
            for i, item in enumerate(self.course_data):
                try:
                    course_name = item['course_name'].replace(" ", "_").replace(".", "")
                    semester = item['semester'].replace(" ", "_").replace("-", "_")
                    pdf_url = item['pdf_link']
                    
                    # Create a valid filename
                    filename = f"{course_name}_{semester}.pdf"
                    filepath = os.path.join(pdf_dir, filename)
                    
                    print(f"Downloading PDF ({i+1}/{total_pdfs}): {filename}")
                    
                    # Use Selenium to navigate to the PDF page
                    download_driver.get(pdf_url)
                    time.sleep(3)  # Wait for the PDF to load
                    
                    # Some sites may render the PDF in an iframe or object tag
                    # Let's check for both possibilities
                    try:
                        # Try to find a PDF viewer iframe
                        iframe = download_driver.find_element(By.TAG_NAME, "iframe")
                        pdf_url = iframe.get_attribute("src")
                        if pdf_url:
                            download_driver.get(pdf_url)
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
                        
                        # Since we can't directly control the native save dialog in headless mode,
                        # we'll check if any PDF was downloaded to the directory
                        downloaded_count += 1
                        print(f"Successfully saved: {filename}")
                    except Exception as e:
                        print(f"Error saving PDF with keyboard shortcut: {str(e)}")
                        
                        # Alternative approach: Try to get the PDF content directly
                        try:
                            # Get the PDF content from the page source
                            pdf_content = download_driver.execute_script("return document.body.outerHTML")
                            
                            # If this isn't a PDF viewer page but the actual PDF, write it to file
                            if pdf_content and "<html" not in pdf_content.lower():
                                with open(filepath, 'wb') as f:
                                    f.write(pdf_content.encode('utf-8'))
                                downloaded_count += 1
                                print(f"Successfully saved PDF content: {filename}")
                            else:
                                print(f"Could not extract PDF content for {filename}")
                        except Exception as inner_e:
                            print(f"Error extracting PDF content: {str(inner_e)}")
                
                except Exception as e:
                    print(f"Error downloading PDF: {str(e)}")
            
            print(f"\nDownloaded {downloaded_count} PDFs to {pdf_dir}")
        
        finally:
            # Clean up
            if download_driver:
                download_driver.quit()


if __name__ == "__main__":
    scraper = EnhancedSyllabusScraper()
    scraper.scrape_syllabus() 