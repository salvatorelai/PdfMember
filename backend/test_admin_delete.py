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

def test_delete_document(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. List Documents to find one to delete or create one?
    # Since we don't have a simple create_document script here, let's pick the last one if available.
    # Ideally, we should create one. But I'll assume we have some.
    response = requests.get(f"{API_URL}/admin/documents", headers=headers)
    documents = response.json()
    
    if not documents:
        print("No documents to delete.")
        return

    # Pick the last one to be safe(ish)
    target_doc = documents[-1]
    doc_id = target_doc['id']
    print(f"Targeting document for deletion: {target_doc['title']} (ID: {doc_id})")

    # 2. Delete
    response = requests.delete(f"{API_URL}/admin/documents/{doc_id}", headers=headers)
    print(f"Delete Status: {response.status_code}")
    
    if response.status_code == 200:
        print("Delete successful.")
        
        # 3. Verify
        response = requests.get(f"{API_URL}/admin/documents", headers=headers)
        new_docs = response.json()
        found = any(d['id'] == doc_id for d in new_docs)
        if not found:
            print("Verification: Document is gone.")
        else:
            print("Verification FAILED: Document still exists.")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    print("Starting Admin Delete Test...")
    token = get_admin_token()
    if token:
        test_delete_document(token)
    print("\nTest Completed.")
