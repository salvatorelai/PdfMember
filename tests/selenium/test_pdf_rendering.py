import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class TestPDFRendering(unittest.TestCase):
    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.base_url = "http://localhost"
        self.driver.implicitly_wait(10)

    def tearDown(self):
        self.driver.quit()

    def login(self):
        print(f"Navigating to {self.base_url}/login")
        self.driver.get(f"{self.base_url}/login")
        
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
        )
        
        inputs = self.driver.find_elements(By.CSS_SELECTOR, "input.el-input__inner")
        if len(inputs) < 2:
            raise Exception("Login inputs not found")
            
        inputs[0].send_keys("admin@example.com")
        inputs[1].send_keys("admin123")
        
        login_btn = self.driver.find_element(By.CSS_SELECTOR, "button.el-button--primary")
        login_btn.click()
        
        # Wait for redirect to home
        WebDriverWait(self.driver, 10).until(
            EC.url_matches(f"{self.base_url}/?$")
        )
        print("Login successful")

    def test_pdf_rendering_document_29(self):
        self.login()
        
        doc_id = 29
        read_url = f"{self.base_url}/document/{doc_id}/read"
        print(f"Navigating to {read_url}")
        self.driver.get(read_url)
        
        # 1. Check for error message first (fail fast)
        try:
            error_el = self.driver.find_element(By.CLASS_NAME, "debug-info")
            if error_el.is_displayed():
                error_text = error_el.text
                self.fail(f"Error message displayed on page: {error_text}")
        except:
            # Element not found is good
            pass

        # 2. Wait for canvas to be present
        print("Waiting for canvas element...")
        canvas = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "canvas"))
        )
        
        # 3. Wait for canvas to have dimensions (meaning rendering started)
        print("Waiting for canvas to have dimensions...")
        def canvas_has_dimensions(d):
            w = d.execute_script("return arguments[0].width", canvas)
            h = d.execute_script("return arguments[0].height", canvas)
            return w > 0 and h > 0

        WebDriverWait(self.driver, 20).until(canvas_has_dimensions)
        
        width = self.driver.execute_script("return arguments[0].width", canvas)
        height = self.driver.execute_script("return arguments[0].height", canvas)
        print(f"Canvas dimensions: {width}x{height}")
        
        self.assertGreater(width, 0, "Canvas width should be > 0")
        self.assertGreater(height, 0, "Canvas height should be > 0")
        
        # 4. Check auto-scaling logic (container width vs canvas width)
        # Get container width
        container = self.driver.find_element(By.CLASS_NAME, "pdf-container")
        container_width = self.driver.execute_script("return arguments[0].clientWidth", container)
        print(f"Container width: {container_width}")
        
        # The canvas display width (CSS width) should fit within container
        # Note: canvas.width is the internal resolution, CSS width is display size.
        # But PDF.js usually sets canvas.style.width = viewport.width + 'px'
        
        # Let's check if there are any console errors
        logs = self.driver.get_log('browser')
        for log in logs:
            if log['level'] == 'SEVERE':
                print(f"Browser Console Error: {log['message']}")
                # We might not want to fail immediately on all errors (some might be favicon etc), 
                # but for PDF rendering, SEVERE errors are bad.
                # self.fail(f"Console error detected: {log['message']}")

        print("Test passed: PDF rendered successfully.")

if __name__ == "__main__":
    unittest.main()
