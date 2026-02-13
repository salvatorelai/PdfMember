import unittest
import time
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class TestAuth(unittest.TestCase):
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

    def test_admin_login(self):
        print("\nTesting Admin Login...")
        self.driver.get(f"{self.base_url}/login")
        
        # Wait for inputs
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.el-input__inner"))
        )
        
        inputs = self.driver.find_elements(By.CSS_SELECTOR, "input.el-input__inner")
        # 0: username, 1: password
        inputs[0].send_keys("admin@example.com")
        inputs[1].send_keys("admin123")
        
        # Click Login
        login_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Login')]")
        login_btn.click()
        
        # Wait for redirect to home
        WebDriverWait(self.driver, 10).until(
            EC.url_matches(f"{self.base_url}/?$")
        )
        print("Redirected to Home")
        
        # Check for user dropdown
        dropdown = self.driver.find_element(By.CLASS_NAME, "el-dropdown-link")
        self.assertTrue(dropdown.is_displayed())
        print("User dropdown found")
        
        # Hover/Click to check for Admin Dashboard
        # In Element Plus, hover triggers dropdown. Or we can just click it.
        dropdown.click()
        time.sleep(1) # Wait for animation
        
        admin_item = self.driver.find_element(By.XPATH, "//li[contains(., 'Admin Dashboard')]")
        self.assertTrue(admin_item.is_displayed())
        print("Admin Dashboard link found")

    def test_invalid_email_registration(self):
        """Test registration with invalid email format"""
        self.driver.get(f"{self.base_url}/login")
        
        # Enter invalid email
        username_input = self.driver.find_element(By.XPATH, "//input[@type='text']")
        password_input = self.driver.find_element(By.XPATH, "//input[@type='password']")
        
        username_input.send_keys("invalid-email")
        password_input.send_keys("password123")
        
        # Click Register
        register_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Register')]")
        register_btn.click()
        
        # Check for error message
        try:
            error_msg = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "el-message--error"))
            )
            print(f"Error message found: {error_msg.text}")
            self.assertIn("valid email", error_msg.text)
        except Exception as e:
            self.fail("Error message for invalid email not found")

    def test_user_registration_and_login(self):
        print("\nTesting User Registration...")
        self.driver.get(f"{self.base_url}/login")
        
        # Generate random user
        rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        email = f"test_{rand_str}@example.com"
        password = "password123"
        
        # Wait for inputs
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.el-input__inner"))
        )
        
        inputs = self.driver.find_elements(By.CSS_SELECTOR, "input.el-input__inner")
        inputs[0].send_keys(email)
        inputs[1].send_keys(password)
        
        # Click Register
        register_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Register')]")
        register_btn.click()
        
        # Wait for success message
        try:
            success_msg = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "el-message--success"))
            )
            print(f"Success message found: {success_msg.text}")
            self.assertTrue(success_msg.is_displayed())
        except Exception as e:
            print("Success message not found or not visible.")
            # Check for error message
            try:
                error_msg = self.driver.find_element(By.CLASS_NAME, "el-message--error")
                print(f"Error message found: {error_msg.text}")
            except:
                print("No error message found either.")
            raise e
        
        print(f"Registration successful for {email}")
        
        # Wait a bit for message to disappear or just proceed
        time.sleep(2)
        
        # Click Login (credentials are still in the inputs)
        # Note: Depending on frontend implementation, inputs might be cleared or not.
        # Looking at index.vue: handleRegister does NOT clear form.
        
        login_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Login')]")
        login_btn.click()
        
        # Wait for redirect to home
        WebDriverWait(self.driver, 10).until(
            EC.url_matches(f"{self.base_url}/?$")
        )
        print("Login successful")
        
        # Check for user dropdown
        dropdown = self.driver.find_element(By.CLASS_NAME, "el-dropdown-link")
        self.assertTrue(dropdown.is_displayed())
        
        # Verify username in dropdown (it usually shows username or 'User')
        # In HomeView.vue: {{ userStore.userInfo?.username || 'User' }}
        # Since we registered with username=email, it should show the email.
        self.assertIn(email, dropdown.text)
        print(f"User {dropdown.text} logged in")

if __name__ == "__main__":
    unittest.main()
