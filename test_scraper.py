#!/usr/bin/env python3
"""
Test script for SRKI scrapers

This script tests the basic functionality of the scrapers without
doing a full crawl or creating output files.
"""

import sys
import time
from urllib.parse import urlparse

try:
    from enhanced_syllabus_scraper import EnhancedSyllabusScraper
    from full_site_scraper import SRKIWebsiteScraper
except ImportError:
    print("Error: Could not import scraper modules. Make sure they are in the same directory.")
    sys.exit(1)

def test_syllabus_scraper():
    """Test the syllabus scraper's ability to access the website and find PDF links."""
    print("\n== Testing Syllabus Scraper ==")
    
    # Create a scraper with a temporary output directory
    scraper = EnhancedSyllabusScraper(output_dir="_test_output")
    
    try:
        # Set headless mode for testing
        scraper.chrome_options.add_argument("--headless")
        scraper.driver.quit()
        scraper.driver = scraper.driver.__class__(
            service=scraper.driver.service,
            options=scraper.chrome_options
        )
        
        # Test ability to access the website
        print("Testing website access...")
        scraper.driver.get(scraper.url)
        
        # Give it a moment to load
        time.sleep(3)
        
        # Check if the page loaded
        if "SRKI" in scraper.driver.title or "Syllabus" in scraper.driver.title:
            print("✓ Successfully accessed syllabus page")
        else:
            print("✗ Failed to access syllabus page correctly")
            print(f"Page title: {scraper.driver.title}")
        
        # Test direct extraction method
        print("Testing PDF extraction...")
        scraper.extract_links_from_source()
        
        # Check if any links were found
        if len(scraper.course_data) > 0:
            print(f"✓ Found {len(scraper.course_data)} syllabus PDF links")
            # Print first 3 links as examples
            for i, item in enumerate(scraper.course_data[:3]):
                print(f"  {i+1}. {item['course_name']} - {item['semester']}")
        else:
            print("✗ No syllabus PDF links found")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {str(e)}")
        return False
    finally:
        # Clean up
        if hasattr(scraper, 'driver') and scraper.driver:
            scraper.driver.quit()

def test_full_website_scraper():
    """Test the full website scraper's ability to access the website and extract data."""
    print("\n== Testing Full Website Scraper ==")
    
    # Create a scraper with a temporary output directory
    scraper = SRKIWebsiteScraper(output_dir="_test_output")
    
    try:
        # Set headless mode for testing
        scraper.chrome_options.add_argument("--headless")
        scraper.driver.quit()
        scraper.driver = scraper.driver.__class__(
            service=scraper.driver.service,
            options=scraper.chrome_options
        )
        
        # Test ability to access the website
        print("Testing website access...")
        scraper.driver.get(scraper.base_url)
        
        # Give it a moment to load
        time.sleep(3)
        
        # Check if the page loaded
        if "SRKI" in scraper.driver.title:
            print("✓ Successfully accessed main website")
        else:
            print("✗ Failed to access website correctly")
            print(f"Page title: {scraper.driver.title}")
        
        # Test link extraction
        print("Testing link extraction...")
        links = scraper.extract_links_from_page(scraper.base_url)
        
        # Check if any links were found
        valid_links = [link for link in links if urlparse(link).netloc == urlparse(scraper.base_url).netloc]
        if len(valid_links) > 0:
            print(f"✓ Found {len(valid_links)} valid links on homepage")
            # Print first 3 links as examples
            for i, link in enumerate(valid_links[:3]):
                print(f"  {i+1}. {link}")
        else:
            print("✗ No valid links found on homepage")
        
        # Test resource extraction
        print("Testing resource extraction...")
        resources = scraper.extract_resources(scraper.base_url)
        
        # Check if any resources were found
        total_resources = len(resources["images"]) + len(resources["pdfs"])
        if total_resources > 0:
            print(f"✓ Found {len(resources['images'])} images and {len(resources['pdfs'])} PDFs")
        else:
            print("✗ No resources found on homepage")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {str(e)}")
        return False
    finally:
        # Clean up
        if hasattr(scraper, 'driver') and scraper.driver:
            scraper.driver.quit()

def main():
    """Run tests for both scrapers."""
    print("=== SRKI Scraper Tests ===")
    
    # Test syllabus scraper
    syllabus_result = test_syllabus_scraper()
    
    # Test full website scraper
    website_result = test_full_website_scraper()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Syllabus Scraper: {'PASSED' if syllabus_result else 'FAILED'}")
    print(f"Full Website Scraper: {'PASSED' if website_result else 'FAILED'}")
    
    if syllabus_result and website_result:
        print("\nAll tests passed! The scrapers appear to be working correctly.")
        return 0
    else:
        print("\nOne or more tests failed. See details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 