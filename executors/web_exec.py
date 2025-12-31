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

class WebExecutor:
    def __init__(self, headless=False):  # Default to VISIBLE browser
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
            else:
                options.add_argument('--start-maximized')  # Open maximized
                options.add_experimental_option("excludeSwitches", ["enable-logging"])
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                print(f"✅ Chrome driver initialized (headless: {self.headless})")
            except Exception as e:
                print(f"❌ Failed to initialize Chrome driver: {e}")
                return None
        
        return self.driver
    
    def open_url(self, url):
        """Open a URL in browser"""
        try:
            driver = self.init_driver()
            if not driver:
                return False
            
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            print(f"🌐 Opening: {url}")
            driver.get(url)
            
            # Wait for page load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            print(f"✅ Opened successfully: {url}")
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
            
            print(f"✅ Extracted {len(text)} chars from {url}")
            return text[:10000]  # Limit length
            
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
            
            print(f"✅ Found {len(results)} results for '{query}'")
            return results
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def take_screenshot(self, filename="screenshot.png"):
        """Take screenshot of current page"""
        try:
            driver = self.init_driver()
            if not driver:
                return None
            
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
            try:
                self.driver.quit()
                self.driver = None
                print("✅ Web driver closed")
            except:
                pass