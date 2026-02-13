import requests

# Configuration
API_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

def get_admin_token():
    response = requests.post(
        f"{API_URL}/auth/login/access-token",
        data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return None
    return response.json()["access_token"]

def test_admin_dashboard(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/admin/stats", headers=headers)
    print(f"\nDashboard Stats Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Stats: {response.json()}")
    else:
        print(f"Error: {response.text}")

def test_user_management(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # List Users
    response = requests.get(f"{API_URL}/admin/users", headers=headers)
    print(f"\nList Users Status: {response.status_code}")
    users = []
    if response.status_code == 200:
        users = response.json()
        print(f"Users found: {len(users)}")
        # print(users)
    else:
        print(f"Error: {response.text}")
        return

    if not users:
        print("No users to update.")
        return

    # Pick a user (not admin if possible) to update
    target_user = None
    for u in users:
        if u["email"] != ADMIN_EMAIL:
            target_user = u
            break
    
    if not target_user:
        print("No non-admin user found to update.")
        # If only admin exists, maybe create a normal user first? 
        # But for now let's just skip update or update self (risky)
        # Let's just create a dummy user first? 
        # Assuming there are users from previous tests.
        return

    print(f"Testing update on user: {target_user['email']} (ID: {target_user['id']})")
    
    # Ban User
    response = requests.put(
        f"{API_URL}/admin/users/{target_user['id']}",
        headers=headers,
        json={"status": "banned"}
    )
    print(f"Ban User Status: {response.status_code}")
    if response.status_code == 200:
        print(f"User status after ban: {response.json()['status']}")
    
    # Activate User
    response = requests.put(
        f"{API_URL}/admin/users/{target_user['id']}",
        headers=headers,
        json={"status": "active"}
    )
    print(f"Activate User Status: {response.status_code}")
    if response.status_code == 200:
        print(f"User status after activate: {response.json()['status']}")

def test_document_management(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # List Documents
    response = requests.get(f"{API_URL}/admin/documents", headers=headers)
    print(f"\nList Documents Status: {response.status_code}")
    documents = []
    if response.status_code == 200:
        documents = response.json()
        print(f"Documents found: {len(documents)}")
    else:
        print(f"Error: {response.text}")
        return

    if not documents:
        print("No documents to update.")
        return

    target_doc = documents[0]
    print(f"Testing update on document: {target_doc['title']} (ID: {target_doc['id']})")

    # Update Status
    original_status = target_doc.get('status', 'draft')
    new_status = 'published' if original_status == 'draft' else 'draft'
    
    response = requests.put(
        f"{API_URL}/admin/documents/{target_doc['id']}",
        headers=headers,
        json={"status": new_status}
    )
    print(f"Update Document Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Document status after update: {response.json()['status']}")
        
        # Revert
        requests.put(
            f"{API_URL}/admin/documents/{target_doc['id']}",
            headers=headers,
            json={"status": original_status}
        )

if __name__ == "__main__":
    print("Starting Admin API Tests...")
    token = get_admin_token()
    if token:
        test_admin_dashboard(token)
        test_user_management(token)
        test_document_management(token)
    print("\nTests Completed.")
