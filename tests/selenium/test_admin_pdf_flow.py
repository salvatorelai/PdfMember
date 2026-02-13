import unittest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class TestAdminPDFFlow(unittest.TestCase):
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
        # Assuming first is email, second is password
        if len(inputs) < 2:
            raise Exception("Login inputs not found")
            
        inputs[0].send_keys("admin@example.com")
        inputs[1].send_keys("admin123")
        
        login_btn = self.driver.find_element(By.CSS_SELECTOR, "button.el-button--primary")
        login_btn.click()
        
        # Wait for redirect to home (root)
        print("Waiting for redirect to home...")
        WebDriverWait(self.driver, 10).until(
            EC.url_matches(f"{self.base_url}/?$")
        )
        print("Redirected to Home")
        
        # Now navigate to admin dashboard
        print("Navigating to Admin Dashboard...")
        self.driver.get(f"{self.base_url}/admin/dashboard")
        
        # Wait for dashboard
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/admin/dashboard")
        )
        print("Login successful and on Dashboard")

    def test_pdf_flow(self):
        try:
            self.login()
            
            # 1. Configure Settings
            print("Navigating to Settings...")
            self.driver.get(f"{self.base_url}/admin/settings")
            time.sleep(2) # Wait for fetch
            
            # Verify we are on settings page
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'System Settings')]"))
            )
            
            # Save Settings (just to test flow)
            save_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Save Settings')]")
            save_btn.click()
            time.sleep(1)
            
            # Check success message
            success_msg = self.driver.find_element(By.CLASS_NAME, "el-message--success")
            self.assertTrue(success_msg.is_displayed())
            print("Settings saved")

            # 2. Create Category
            print("Navigating to Categories...")
            self.driver.get(f"{self.base_url}/admin/categories")
            time.sleep(2)
            
            # Add Category
            self.driver.find_element(By.XPATH, "//button[contains(., 'Add Category')]").click()
            time.sleep(1)
            
            # Fill form
            dialog = self.driver.find_element(By.CSS_SELECTOR, ".el-dialog")
            name_input = dialog.find_element(By.CSS_SELECTOR, "input.el-input__inner")
            cat_name = f"Selenium_PDF_{int(time.time())}"
            name_input.send_keys(cat_name)
            
            dialog.find_element(By.XPATH, "//button[contains(., 'Confirm')]").click()
            time.sleep(1)
            print(f"Category {cat_name} created")

            # 3. Batch Upload
            print("Navigating to Documents...")
            self.driver.get(f"{self.base_url}/admin/documents")
            time.sleep(2)
            
            self.driver.find_element(By.XPATH, "//button[contains(., 'Batch Upload')]").click()
            time.sleep(1)
            
            # Upload Dialog - getting the visible one
            dialogs = self.driver.find_elements(By.CSS_SELECTOR, ".el-dialog")
            # Filter for the visible one
            dialog = None
            for d in dialogs:
                if d.is_displayed():
                    dialog = d
                    break
            
            if not dialog:
                dialog = dialogs[-1] # Fallback
            
            # Select Category
            dialog.find_element(By.CSS_SELECTOR, ".el-select").click()
            time.sleep(1)
            
            # Select the category
            options = self.driver.find_elements(By.CSS_SELECTOR, ".el-select-dropdown__item")
            found_cat = False
            for opt in options:
                if cat_name in opt.text:
                    opt.click()
                    found_cat = True
                    break
            
            if not found_cat and options:
                options[0].click()
                print("Warning: specific category not found, selected first available.")

            # Upload File
            file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            pdf_path = os.path.abspath("test_doc.pdf")
            print(f"Uploading file from: {pdf_path}")
            if not os.path.exists(pdf_path):
                print("ERROR: Test file does not exist!")
            file_input.send_keys(pdf_path)
            
            # Verify file selection via JS
            file_count = self.driver.execute_script("return arguments[0].files.length", file_input)
            print(f"Selected files count: {file_count}")
            
            # Click Upload in the dialog
            upload_btns = dialog.find_elements(By.XPATH, ".//button[contains(., 'Upload')]")
            if upload_btns:
                upload_btns[-1].click()
            
            # Wait for success message
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "el-message--success"))
                )
                print("Batch upload successful")
            except Exception as e:
                print("Timeout waiting for success message. Checking for errors...")
                # Check for error/warning messages
                errors = self.driver.find_elements(By.CLASS_NAME, "el-message--error")
                for err in errors:
                    print(f"Error Message: {err.text}")
                warnings = self.driver.find_elements(By.CLASS_NAME, "el-message--warning")
                for warn in warnings:
                    print(f"Warning Message: {warn.text}")
                
                # Check console logs
                logs = self.driver.get_log('browser')
                for log in logs:
                    print(f"Console Log: {log}")
                
                raise e

            time.sleep(2) # Wait for table refresh

            # 4. Verify Document and Share
            rows = self.driver.find_elements(By.CSS_SELECTOR, ".el-table__body tr")
            target_row = None
            for row in rows:
                if "test_doc.pdf" in row.text:
                    target_row = row
                    break
            
            self.assertIsNotNone(target_row, "Uploaded document not found in table")
            print("Document found in table")
            
            # Click Share
            share_btn = target_row.find_element(By.XPATH, ".//button[contains(., 'Share')]")
            share_btn.click()
            time.sleep(1)
            
            # Share Dialog
            share_dialogs = self.driver.find_elements(By.CSS_SELECTOR, ".el-dialog")
            share_dialog = None
            for d in share_dialogs:
                if d.is_displayed() and "Share" in d.text:
                    share_dialog = d
                    break
            if not share_dialog:
                share_dialog = share_dialogs[-1]
            
            # Generate Link
            gen_btn = share_dialog.find_element(By.XPATH, ".//button[contains(., 'Generate')]")
            gen_btn.click()
            
            time.sleep(1)
            
            # Verify Link Display
            links = share_dialog.find_elements(By.CSS_SELECTOR, "a")
            self.assertTrue(len(links) > 0)
            link_url = links[0].get_attribute("href")
            print(f"Generated Secure Link: {link_url}")
            
            # 5. Verify Download Page
            self.driver.execute_script(f"window.open('{link_url}', '_blank');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            time.sleep(2)
            # Check if we are on download page
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Secure Download')]"))
            )
            print("Secure Download page verified")
            
            # Check file info
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            self.assertTrue("test_doc.pdf" in body_text)
            
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

        except Exception as e:
            timestamp = int(time.time())
            self.driver.save_screenshot(f"error_screenshot_{timestamp}.png")
            with open(f"error_source_{timestamp}.html", "w") as f:
                f.write(self.driver.page_source)
            print(f"Test failed. URL: {self.driver.current_url}")
            print(f"Saved screenshot to error_screenshot_{timestamp}.png")
            print(f"Saved source to error_source_{timestamp}.html")
            raise e

if __name__ == "__main__":
    unittest.main()
