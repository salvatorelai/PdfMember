import requests
import sys

BASE_URL = "http://localhost"
EMAIL = "admin@example.com"
PASSWORD = "admin123"

def login():
    resp = requests.post(f"{BASE_URL}/api/v1/auth/login/access-token", data={
        "username": EMAIL,
        "password": PASSWORD
    })
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        sys.exit(1)
    return resp.json()["access_token"]

def upload(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Create a dummy PDF if test_doc.pdf doesn't exist, but it should exist
    files = [
        ('files', ('test_doc.pdf', open('test_doc.pdf', 'rb'), 'application/pdf'))
    ]
    data = {
        'category_id': 2 # Assuming category 2 exists from previous logs
    }
    
    print("Uploading...")
    resp = requests.post(f"{BASE_URL}/api/v1/admin/upload/batch", headers=headers, files=files, data=data)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")

if __name__ == "__main__":
    token = login()
    upload(token)
