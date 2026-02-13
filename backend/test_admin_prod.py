import requests
import sys

# Configuration
API_URL = "http://localhost/api/v1"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

def get_admin_token():
    print(f"Logging in as {ADMIN_EMAIL}...")
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

def test_admin_dashboard(token):
    print("\nTesting Dashboard Stats...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/admin/stats", headers=headers)
    print(f"Dashboard Stats Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Stats: {response.json()}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_category_management(token):
    print("\nTesting Category Management...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # List
    print("1. Listing categories...")
    response = requests.get(f"{API_URL}/documents/categories", headers=headers)
    if response.status_code != 200:
        print(f"List failed: {response.status_code} {response.text}")
        return False
    
    # Create
    print("2. Creating category...")
    new_cat = {
        "name": "Test Category",
        "slug": "test-category",
        "description": "Created by test script",
        "sort_order": 10
    }
    response = requests.post(f"{API_URL}/documents/categories", headers=headers, json=new_cat)
    if response.status_code not in [200, 201]:
        print(f"Create failed: {response.status_code} {response.text}")
        # It might already exist, so let's try to find it
    else:
        print(f"Created: {response.json()['id']}")
        cat_id = response.json()['id']
        
        # Update
        print(f"3. Updating category {cat_id}...")
        update_data = {"name": "Test Category Updated", "slug": "test-category"}
        response = requests.put(f"{API_URL}/documents/categories/{cat_id}", headers=headers, json=update_data)
        if response.status_code != 200:
            print(f"Update failed: {response.status_code} {response.text}")
            return False
        print("Updated successfully")
        
        # Delete
        print(f"4. Deleting category {cat_id}...")
        response = requests.delete(f"{API_URL}/documents/categories/{cat_id}", headers=headers)
        if response.status_code != 200:
            print(f"Delete failed: {response.status_code} {response.text}")
            return False
        print("Deleted successfully")

    return True

if __name__ == "__main__":
    token = get_admin_token()
    if token:
        success = test_admin_dashboard(token)
        if success:
            test_category_management(token)
