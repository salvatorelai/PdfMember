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

class TestCategoryManagement(unittest.TestCase):
    def setUp(self):
        chrome_options = Options()
        # Uncomment the following line to run in headless mode
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            service = Service(ChromeDriverManager().install())
        except Exception:
            # Fallback for environments where webdriver_manager fails (e.g. offline)
            # Assumes chromedriver is in PATH
            service = Service()

        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.base_url = os.getenv("TEST_URL", "http://localhost")
        self.timestamp = int(time.time())

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_create_category_with_parent(self):
        """
        Test Case:
        1. Login as Admin
        2. Create a Parent Category
        3. Create a Child Category linked to the Parent
        4. Verify display in table
        """
        driver = self.driver
        wait = WebDriverWait(driver, 10)

        print("\n=== Starting Category Management Test ===")

        # 1. Login
        print("[1/7] Logging in...")
        driver.get(f"{self.base_url}/login")
        
        # Element Plus input for username defaults to type='text'
        # We can find it by type='text' or by the label
        username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
        username_input.send_keys("admin@example.com")
        
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_input.send_keys("admin123")
        
        # Element Plus button might not have type='submit'
        login_btn = driver.find_element(By.XPATH, "//button[contains(., 'Login')]")
        login_btn.click()
        
        # Wait for login to complete (url changes from /login)
        wait.until(lambda d: d.current_url != f"{self.base_url}/login")
        print("      Login successful (redirected).")

        # 2. Navigate to Categories
        print("[2/7] Navigating to Categories page...")
        driver.get(f"{self.base_url}/admin/categories")
        
        # 3. Create Parent Category
        print("[3/7] Creating Parent Category...")
        parent_name = f"Parent_Test_{self.timestamp}"
        parent_slug = f"parent-test-{self.timestamp}"
        
        add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Add Category')]")))
        add_btn.click()
        
        # Wait for dialog
        dialog = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".el-dialog")))
        
        # Fill form
        # Use .// to search inside dialog
        # Find form first to be safe
        form = dialog.find_element(By.TAG_NAME, "form")
        inputs = form.find_elements(By.TAG_NAME, "input")
        
        # 1. Name (1st input)
        name_input = inputs[0]
        name_input.send_keys(parent_name)
        
        # 2. Slug (2nd input)
        slug_input = inputs[1]
        slug_input.send_keys(parent_slug)
        
        confirm_btn = dialog.find_element(By.XPATH, ".//button[contains(., 'Confirm')]")
        confirm_btn.click()
        
        # Wait for reload/update
        time.sleep(2)
        driver.refresh()
        
        # 4. Verify Parent Exists
        print(f"      Verifying Parent Category '{parent_name}' exists...")
        wait.until(EC.presence_of_element_located((By.XPATH, f"//div[contains(text(), '{parent_name}')]")))
        
        # 5. Create Child Category
        print("[5/7] Creating Child Category...")
        child_name = f"Child_Test_{self.timestamp}"
        child_slug = f"child-test-{self.timestamp}"
        
        add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Add Category')]")))
        add_btn.click()
        
        # Wait for dialog
        dialog = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".el-dialog")))
        
        # Fill form
        form = dialog.find_element(By.TAG_NAME, "form")
        inputs = form.find_elements(By.TAG_NAME, "input")
        
        name_input = inputs[0]
        name_input.clear() # Clear just in case
        name_input.send_keys(child_name)
        
        slug_input = inputs[1]
        slug_input.clear()
        slug_input.send_keys(child_slug)
        
        # Select Parent
        print("      Selecting Parent from dropdown...")
        
        # Robust selector: Find el-form-item containing 'Parent' label, then find el-select inside it
        try:
            # Check Dialog Title
            title_el = dialog.find_element(By.CSS_SELECTOR, ".el-dialog__title")
            print(f"DEBUG: Dialog Title: '{title_el.text}'")
            
            # Check if Parent label exists
            labels = dialog.find_elements(By.TAG_NAME, "label")
            label_texts = [l.text for l in labels]
            print(f"DEBUG: Labels found in dialog: {label_texts}")

            # Try finding by label text traversing up to form-item
            parent_select = dialog.find_element(By.XPATH, ".//div[contains(@class, 'el-form-item')][.//label[contains(., 'Parent')]]//div[contains(@class, 'el-select')]")
        except Exception:
            # Fallback: Print dialog content for debugging
            print(f"DEBUG: Dialog Text Content: {dialog.text}")
            print(f"DEBUG: Dialog HTML: {dialog.get_attribute('innerHTML')}")
            # Try finding by placeholder (if visible in input)
            try:
                parent_select = dialog.find_element(By.XPATH, ".//input[@placeholder='Select Parent Category']")
                # If we found the input, we usually need to click the wrapper (parent)
                parent_select = parent_select.find_element(By.XPATH, "./ancestor::div[contains(@class, 'el-select')]")
            except:
                raise

        parent_select.click()
        
        # Wait for dropdown options (attached to body)
        # Note: Select dropdown is attached to body, so we use driver.find_element (default) or explicit wait
        option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[contains(@class, 'el-select-dropdown__item') and contains(., '{parent_name}')]")))
        option.click()
        
        confirm_btn = dialog.find_element(By.XPATH, ".//button[contains(., 'Confirm')]")
        confirm_btn.click()
        
        # Wait for reload/update
        time.sleep(2)
        driver.refresh()
        
        # 6. Verify Child Exists
        print(f"[6/7] Verifying Child Category '{child_name}' exists...")
        wait.until(EC.presence_of_element_located((By.XPATH, f"//div[contains(text(), '{child_name}')]")))
        
        # 7. Verify Parent Link in Table
        print(f"[7/7] Verifying Parent Link in table...")
        # Find row containing child
        child_row = driver.find_element(By.XPATH, f"//tr[.//div[contains(text(), '{child_name}')]]")
        
        # Assert parent name is visible in that row
        if parent_name in child_row.text:
            print("      SUCCESS: Parent name found in child row.")
        else:
            self.fail(f"Parent name '{parent_name}' not found in child row. Row text: {child_row.text}")

        print("\n=== Test Passed Successfully ===")

if __name__ == "__main__":
    unittest.main()
