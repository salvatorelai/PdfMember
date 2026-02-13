import requests

API_URL = "http://localhost:8000/api/v1"

def test_documents():
    # 1. Login to get token
    print("Logging in...")
    login_data = {
        "username": "testuser", # email in db is test@example.com but auth uses username field for lookup
        "password": "password123"
    }
    response = requests.post(f"{API_URL}/auth/login/access-token", data=login_data)
    if response.status_code != 200:
        print("Login failed:", response.text)
        return
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Logged in.")

    # 2. Create Category
    print("\nCreating Category...")
    import time
    timestamp = int(time.time())
    cat_data = {
        "name": f"Technology {timestamp}",
        "slug": f"technology-{timestamp}",
        "description": "Tech docs"
    }
    response = requests.post(f"{API_URL}/documents/categories", json=cat_data, headers=headers)
    if response.status_code == 200:
        cat_id = response.json()["id"]
        print("Category created:", cat_id)
    elif response.status_code == 400 and "IntegrityError" in response.text:
         # Assuming slug unique constraint
         print("Category might already exist, proceeding.")
         # Fetch it
         response = requests.get(f"{API_URL}/documents/categories", headers=headers)
         cat_id = response.json()[0]["id"]
    else:
        print("Create Category failed:", response.text)
        return

    # 3. Upload File
    print("\nUploading File...")
    files = {'file': ('test.pdf', b'%PDF-1.4 empty pdf content', 'application/pdf')}
    response = requests.post(f"{API_URL}/documents/upload", files=files, headers=headers)
    if response.status_code != 200:
        print("Upload failed:", response.text)
        return
    upload_data = response.json()
    print("File uploaded:", upload_data)

    # 4. Create Document
    print("\nCreating Document...")
    doc_data = {
        "title": "My First PDF",
        "description": "This is a test PDF",
        "category_id": cat_id,
        "file_path": upload_data["file_path"],
        "file_name": upload_data["file_name"],
        "file_size": upload_data["file_size"],
        "status": "published"
    }
    response = requests.post(f"{API_URL}/documents/", json=doc_data, headers=headers)
    if response.status_code != 200:
        print("Create Document failed:", response.text)
        return
    doc_id = response.json()["id"]
    print("Document created:", doc_id)

    # 5. List Documents
    print("\nListing Documents...")
    response = requests.get(f"{API_URL}/documents/", headers=headers)
    docs = response.json()
    print(f"Found {len(docs)} documents")
    print(docs[0] if docs else "No docs")

if __name__ == "__main__":
    test_documents()
