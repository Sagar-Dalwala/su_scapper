import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class SUSyllabusScraper:
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
    
    def extract_course_links(self, course_type="undergraduate"):
        """Extract links for each course under the specified course type."""
        course_data = []
        
        try:
            # Wait for the page to load
            self.wait_for_element(By.CSS_SELECTOR, ".container")
            
            # Find and click the appropriate course type button
            if course_type.lower() == "undergraduate":
                # Undergraduate courses are shown by default, no need to click
                course_section = self.driver.find_element(By.XPATH, "//h3[contains(text(), 'Under Graduate Courses')]/..")
            else:
                # For postgraduate, need to find that section
                course_section = self.driver.find_element(By.XPATH, "//h3[contains(text(), 'Post Graduate Courses')]/..")
            
            # Find all course links within the section
            course_links = course_section.find_elements(By.CSS_SELECTOR, "a")
            
            # Extract course names for later clicking
            courses = []
            for link in course_links:
                course_name = link.text.strip()
                if course_name:  # Only add non-empty course names
                    courses.append(course_name)
            
            # Process each course
            for course in courses:
                try:
                    # Find and click on the course
                    course_element = self.driver.find_element(By.XPATH, f"//a[contains(text(), '{course}')]")
                    course_element.click()
                    time.sleep(2)  # Wait for table to load
                    
                    # Find the semester table
                    tables = self.driver.find_elements(By.TAG_NAME, "table")
                    
                    if tables:
                        # Find the table related to this course
                        for table in tables:
                            # Extract semester links from the table
                            semester_links = table.find_elements(By.TAG_NAME, "a")
                            
                            for link in semester_links:
                                href = link.get_attribute("href")
                                text = link.text.strip()
                                
                                if href and href.endswith(".pdf"):
                                    course_data.append({
                                        "course_type": course_type,
                                        "course_name": course,
                                        "semester": text,
                                        "pdf_link": href
                                    })
                    else:
                        print(f"No tables found for {course}")
                
                except NoSuchElementException:
                    print(f"Could not find course element for {course}")
                except Exception as e:
                    print(f"Error processing course {course}: {str(e)}")
        
        except Exception as e:
            print(f"Error extracting course links: {str(e)}")
        
        return course_data
    
    def scrape_syllabus(self):
        """Main method to scrape all syllabus data."""
        try:
            # Navigate to the syllabus page
            self.driver.get(self.url)
            time.sleep(3)  # Wait for page to load completely
            
            # Get undergraduate courses
            print("Scraping undergraduate courses...")
            undergraduate_data = self.extract_course_links("undergraduate")
            
            # Get postgraduate courses
            print("Scraping postgraduate courses...")
            postgraduate_data = self.extract_course_links("postgraduate")
            
            # Combine all data
            all_data = undergraduate_data + postgraduate_data
            
            # Save data to CSV
            self.save_to_csv(all_data)
            
            print(f"Scraping completed. Found {len(all_data)} syllabus links.")
            
        except Exception as e:
            print(f"Error during scraping: {str(e)}")
        finally:
            # Clean up
            self.driver.quit()
    
    def save_to_csv(self, data):
        """Save the scraped data to a CSV file."""
        csv_path = os.path.join(self.output_dir, "syllabus_links.csv")
        
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['course_type', 'course_name', 'semester', 'pdf_link']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for row in data:
                    writer.writerow(row)
            
            print(f"Data saved to {csv_path}")
        
        except Exception as e:
            print(f"Error saving to CSV: {str(e)}")

    def download_pdfs(self, data):
        """Download the PDF files (optional functionality)."""
        pdf_dir = os.path.join(self.output_dir, "pdfs")
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)
        
        import requests
        
        for item in data:
            try:
                course_name = item['course_name'].replace(" ", "_")
                semester = item['semester'].replace(" ", "_").replace("-", "_")
                pdf_url = item['pdf_link']
                
                # Create a valid filename
                filename = f"{course_name}_{semester}.pdf"
                filepath = os.path.join(pdf_dir, filename)
                
                # Download the PDF
                response = requests.get(pdf_url, stream=True)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"Downloaded {filename}")
                else:
                    print(f"Failed to download {pdf_url}, status code: {response.status_code}")
            
            except Exception as e:
                print(f"Error downloading PDF: {str(e)}")


if __name__ == "__main__":
    scraper = SUSyllabusScraper()
    scraper.scrape_syllabus() 