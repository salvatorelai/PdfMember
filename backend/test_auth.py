import requests
import sys

API_URL = "http://localhost:8000/api/v1"

def test_auth():
    # 1. Register
    print("Testing Registration...")
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    }
    
    # Check if user already exists or clean up? 
    # For now, let's just try to register. If 400, assumes exists and proceed to login.
    response = requests.post(f"{API_URL}/auth/register", json=user_data)
    if response.status_code == 200:
        print("Registration successful:", response.json())
    elif response.status_code == 400 and "exists" in response.text:
        print("User already exists, proceeding to login.")
    else:
        print("Registration failed:", response.status_code, response.text)
        # return

    # 2. Login
    print("\nTesting Login...")
    login_data = {
        "username": "test@example.com", # Auth endpoint checks email too in our logic
        "password": "password123"
    }
    response = requests.post(f"{API_URL}/auth/login/access-token", data=login_data)
    if response.status_code != 200:
        print("Login failed:", response.status_code, response.text)
        return
    
    token_data = response.json()
    print("Login successful. Token:", token_data["access_token"][:20] + "...")
    access_token = token_data["access_token"]

    # 3. Test Token
    print("\nTesting Token Access...")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(f"{API_URL}/auth/test-token", headers=headers)
    if response.status_code == 200:
        print("Token validation successful. User:", response.json())
    else:
        print("Token validation failed:", response.status_code, response.text)

if __name__ == "__main__":
    test_auth()
