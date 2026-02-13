import requests
import sys

# Configuration
API_URL = "http://localhost/api/v1"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

def get_admin_token():
    try:
        response = requests.post(
            f"{API_URL}/auth/login/access-token",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        )
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            return None
        return response.json()["access_token"]
    except Exception as e:
        print(f"Login request failed: {e}")
        return None

def test_category_hierarchy(token):
    print("\nTesting Category Hierarchy...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create Parent
    print("1. Creating Parent Category...")
    parent_data = {
        "name": "Parent Cat",
        "slug": "parent-cat",
        "description": "Parent",
        "sort_order": 1
    }
    response = requests.post(f"{API_URL}/documents/categories", headers=headers, json=parent_data)
    if response.status_code not in [200, 201]:
        print(f"Create Parent failed: {response.text}")
        return False
    parent_id = response.json()['id']
    print(f"Parent Created: {parent_id}")
    
    # 2. Create Child
    print("2. Creating Child Category...")
    child_data = {
        "name": "Child Cat",
        "slug": "child-cat",
        "description": "Child",
        "parent_id": parent_id,
        "sort_order": 2
    }
    response = requests.post(f"{API_URL}/documents/categories", headers=headers, json=child_data)
    if response.status_code not in [200, 201]:
        print(f"Create Child failed: {response.text}")
        return False
    child_id = response.json()['id']
    print(f"Child Created: {child_id}")
    
    # 3. Verify Child has Parent
    if response.json().get('parent_id') != parent_id:
        print(f"Error: Child parent_id mismatch. Expected {parent_id}, got {response.json().get('parent_id')}")
        return False
    print("Child correctly linked to Parent")
    
    # Clean up
    print("Cleaning up...")
    requests.delete(f"{API_URL}/documents/categories/{child_id}", headers=headers)
    requests.delete(f"{API_URL}/documents/categories/{parent_id}", headers=headers)
    print("Cleanup done")
    
    return True

if __name__ == "__main__":
    token = get_admin_token()
    if token:
        test_category_hierarchy(token)
