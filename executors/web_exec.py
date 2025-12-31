# executors/web_exec.py
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os
import json

class WebExecutor:
    def __init__(self, headless=True):
        self.driver = None
        self.headless = headless
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def init_driver(self):
        """Initialize Chrome driver if not already done"""
        if self.driver is None:
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        
        return self.driver
    
    def open_url(self, url):
        """Open a URL in browser"""
        try:
            driver = self.init_driver()
            
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            print(f"✅ Opened: {url}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to open {url}: {e}")
            return False
    
    def get_page_content(self, url):
        """Get page content via requests (faster than selenium)"""
        try:
            if not url.startswith('http'):
                url = 'https://' + url
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove scripts and styles
            for tag in soup(["script", "style", "nav", "footer", "aside"]):
                tag.decompose()
            
            # Get clean text
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text[:3000]  # Limit length
            
        except Exception as e:
            print(f"❌ Failed to get content: {e}")
            return None
    
    def search_google(self, query, num_results=5):
        """Search Google and return results"""
        try:
            search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Extract search results
            for g in soup.find_all('div', {'class': 'g'}):
                link = g.find('a', href=True)
                title = g.find('h3')
                
                if link and title:
                    result = {
                        'title': title.text,
                        'url': link['href'],
                        'summary': g.get_text()[:150] + '...'
                    }
                    results.append(result)
                    
                    if len(results) >= num_results:
                        break
            
            return results
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def take_screenshot(self, filename="screenshot.png"):
        """Take screenshot of current page"""
        try:
            driver = self.init_driver()
            
            # Ensure AutoBox/AB1 exists
            screenshot_dir = os.path.join("AutoBox", "AB1")
            os.makedirs(screenshot_dir, exist_ok=True)
            
            filepath = os.path.join(screenshot_dir, filename)
            driver.save_screenshot(filepath)
            
            print(f"✅ Screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            return None
    
    def close(self):
        """Close driver if open"""
        if self.driver:
            self.driver.quit()
            self.driver = None

# Singleton instance
web_executor = WebExecutor()