import time
import unittest
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class TestFrontendCategoryDisplay(unittest.TestCase):
    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            service = Service(ChromeDriverManager().install())
        except Exception:
            service = Service()

        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.base_url = os.getenv("TEST_URL", "http://localhost")
        self.timestamp = int(time.time())

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_child_category_display(self):
        """
        Test Case:
        1. Login as Admin
        2. Create Parent and Child Category
        3. Go to Home Page
        4. Verify Parent Category is displayed
        5. Expand Parent and verify Child Category is displayed
        """
        driver = self.driver
        wait = WebDriverWait(driver, 10)

        print("\n=== Starting Frontend Category Display Test ===")

        # 1. Login and Create Categories (Reuse logic or do it quickly)
        print("[1/5] Logging in as Admin...")
        driver.get(f"{self.base_url}/login")
        
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))).send_keys("admin@example.com")
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys("admin123")
        driver.find_element(By.XPATH, "//button[contains(., 'Login')]").click()
        wait.until(lambda d: d.current_url != f"{self.base_url}/login")

        # 2. Create Categories
        print("[2/5] Creating Test Categories...")
        driver.get(f"{self.base_url}/admin/categories")
        
        parent_name = f"F_Parent_{self.timestamp}"
        child_name = f"F_Child_{self.timestamp}"
        
        # Create Parent
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Add Category')]"))).click()
        dialog = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".el-dialog")))
        dialog.find_element(By.TAG_NAME, "form").find_elements(By.TAG_NAME, "input")[0].send_keys(parent_name)
        dialog.find_element(By.TAG_NAME, "form").find_elements(By.TAG_NAME, "input")[1].send_keys(f"fp-{self.timestamp}")
        dialog.find_element(By.XPATH, ".//button[contains(., 'Confirm')]").click()
        time.sleep(1)
        driver.refresh()
        
        # Create Child
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Add Category')]"))).click()
        dialog = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".el-dialog")))
        dialog.find_element(By.TAG_NAME, "form").find_elements(By.TAG_NAME, "input")[0].send_keys(child_name)
        dialog.find_element(By.TAG_NAME, "form").find_elements(By.TAG_NAME, "input")[1].send_keys(f"fc-{self.timestamp}")
        
        # Select Parent
        try:
            parent_select = dialog.find_element(By.XPATH, ".//div[contains(@class, 'el-form-item')][.//label[contains(., 'Parent')]]//div[contains(@class, 'el-select')]")
        except:
            parent_select = dialog.find_element(By.XPATH, ".//input[@placeholder='Select Parent Category']").find_element(By.XPATH, "./ancestor::div[contains(@class, 'el-select')]")
        
        parent_select.click()
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[contains(., '{parent_name}')]"))).click()
        
        dialog.find_element(By.XPATH, ".//button[contains(., 'Confirm')]").click()
        time.sleep(1)

        # 3. Go to Home Page
        print("[3/5] Navigating to Home Page...")
        driver.get(self.base_url)
        time.sleep(2) # Wait for categories to load

        # 4. Verify Parent Display
        print(f"[4/5] Verifying Parent '{parent_name}' display...")
        # Check if parent exists in menu. Note: el-sub-menu title might be inside a template
        # We look for the text
        parent_el = wait.until(EC.visibility_of_element_located((By.XPATH, f"//span[contains(text(), '{parent_name}')]")))
        print("      Parent category found.")

        # 5. Expand and Verify Child
        print(f"[5/5] Expanding Parent and verifying Child '{child_name}'...")
        # Click parent to expand (it's a sub-menu now)
        # We need to click the el-sub-menu__title which contains the text
        parent_menu_item = parent_el.find_element(By.XPATH, "./ancestor::div[@class='el-sub-menu__title']")
        parent_menu_item.click()
        
        # Wait for animation
        time.sleep(1)
        
        # Check child
        child_el = wait.until(EC.visibility_of_element_located((By.XPATH, f"//span[contains(text(), '{child_name}')]")))
        print("      Child category found.")
        
        print("\n=== Test Passed Successfully ===")

if __name__ == "__main__":
    unittest.main()
