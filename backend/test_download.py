import asyncio
import requests
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from sqlalchemy import select
from app.core.security import get_password_hash

BASE_URL = "http://localhost:8000/api/v1"

# Test Users
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"
USER_EMAIL = "test_dl@example.com"
USER_PASSWORD = "password123"

async def setup_admin():
    async with SessionLocal() as db:
        # Check if admin exists
        result = await db.execute(select(User).filter(User.email == ADMIN_EMAIL))
        user = result.scalars().first()
        
        if not user:
            print("Creating admin user...")
            user = User(
                email=ADMIN_EMAIL,
                username="admin",
                password_hash=get_password_hash(ADMIN_PASSWORD),
                role=UserRole.SUPER_ADMIN,
                status="active"
            )
            db.add(user)
            await db.commit()
            print("Admin user created.")
        else:
            if user.role != UserRole.SUPER_ADMIN:
                user.role = UserRole.SUPER_ADMIN
                await db.commit()
                print("Admin role updated.")

def get_token(email, password):
    response = requests.post(
        f"{BASE_URL}/auth/login/access-token",
        data={"username": email, "password": password}
    )
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return None
    return response.json()["access_token"]

def test_download_flow():
    print("--- Testing Download Flow ---")
    
    # 0. Setup Admin
    asyncio.run(setup_admin())
    
    # 1. Login as Admin
    admin_token = get_token(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not admin_token:
        return
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    
    # Check if we have documents
    res = requests.get(f"{BASE_URL}/documents/", headers=headers_admin)
    documents = res.json()
    
    doc_id = None
    if not documents:
        # Create a dummy document
        print("Creating dummy document...")
        # Upload file first
        files = {'file': ('test.pdf', b'Dummy PDF content', 'application/pdf')}
        upload_res = requests.post(f"{BASE_URL}/documents/upload", headers=headers_admin, files=files)
        file_data = upload_res.json()
        
        # Create doc record
        doc_data = {
            "title": "Test Download Doc",
            "file_path": file_data["file_path"],
            "file_name": file_data["file_name"],
            "file_size": file_data["file_size"],
            "status": "published"
        }
        create_res = requests.post(f"{BASE_URL}/documents/", headers=headers_admin, json=doc_data)
        doc_id = create_res.json()["id"]
        print(f"Created document ID: {doc_id}")
    else:
        doc_id = documents[0]["id"]
        print(f"Using existing document ID: {doc_id}")
        
    # 2. Login as Normal User
    user_token = get_token(USER_EMAIL, USER_PASSWORD)
    if not user_token:
        # Register if not exists
        print("Registering new user...")
        reg_res = requests.post(f"{BASE_URL}/auth/register", json={
            "email": USER_EMAIL, "password": USER_PASSWORD, "username": "testuser_dl"
        })
        if reg_res.status_code == 200:
            user_token = get_token(USER_EMAIL, USER_PASSWORD)
        else:
            print(f"Registration failed: {reg_res.text}")
            # Try to login again, maybe user exists
            user_token = get_token(USER_EMAIL, USER_PASSWORD)
            
    headers_user = {"Authorization": f"Bearer {user_token}"}
    
    # 3. Check Membership
    mem_res = requests.get(f"{BASE_URL}/membership/me", headers=headers_user)
    membership = mem_res.json()
    print(f"Initial Membership: Type={membership['type']}, Quota={membership['download_used']}/{membership['download_quota']}")
    
    initial_used = membership['download_used']
    
    # 4. Download Document
    print(f"Attempting download document {doc_id}...")
    dl_res = requests.get(f"{BASE_URL}/documents/{doc_id}/download", headers=headers_user)
    
    if dl_res.status_code == 200:
        print("Download successful!")
        print(f"URL: {dl_res.json()['url']}")
        
        # 5. Check Quota Update
        mem_res_after = requests.get(f"{BASE_URL}/membership/me", headers=headers_user)
        membership_after = mem_res_after.json()
        print(f"Updated Membership: Type={membership_after['type']}, Quota={membership_after['download_used']}/{membership_after['download_quota']}")
        
        if membership_after['download_used'] == initial_used + 1:
            print("SUCCESS: Quota decremented correctly.")
        else:
            print("FAILURE: Quota not updated.")
            
    elif dl_res.status_code == 403:
        print("Download blocked as expected (Quota exceeded or Expired).")
    else:
        print(f"Download failed with unexpected error: {dl_res.status_code} - {dl_res.text}")

if __name__ == "__main__":
    test_download_flow()
