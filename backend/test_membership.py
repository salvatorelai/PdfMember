import asyncio
import requests
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from sqlalchemy import select, update
from app.core.security import get_password_hash

API_URL = "http://localhost:8000/api/v1"

async def setup_admin():
    async with SessionLocal() as db:
        # Check if admin exists
        result = await db.execute(select(User).filter(User.email == "admin@example.com"))
        user = result.scalars().first()
        
        if not user:
            print("Creating admin user...")
            user = User(
                email="admin@example.com",
                username="admin",
                password_hash=get_password_hash("admin123"),
                role=UserRole.SUPER_ADMIN,
                status="active"
            )
            db.add(user)
            await db.commit()
            print("Admin user created.")
        else:
            print("Admin user exists. Ensuring Super Admin role...")
            if user.role != UserRole.SUPER_ADMIN:
                user.role = UserRole.SUPER_ADMIN
                await db.commit()
            print("Admin role updated.")

def test_membership_flow():
    # 1. Login as Admin
    print("\n1. Login as Admin")
    response = requests.post(f"{API_URL}/auth/login/access-token", data={
        "username": "admin@example.com",
        "password": "admin123"
    })
    if response.status_code != 200:
        print(f"Admin login failed: {response.text}")
        return
    admin_token = response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("Admin logged in.")

    # 2. Create Redeem Code
    print("\n2. Create Redeem Code")
    code_data = {
        "code": "VIP-2024",
        "type": "lifetime",
        "uses_total": 10
    }
    response = requests.post(f"{API_URL}/membership/codes", json=code_data, headers=admin_headers)
    if response.status_code == 200:
        print(f"Code created: {response.json()}")
    elif response.status_code == 400 and "already exists" in response.text:
        print("Code already exists, proceeding...")
    else:
        print(f"Failed to create code: {response.text}")
        return

    # 3. Register/Login as User
    print("\n3. Login as User")
    # Try login first
    response = requests.post(f"{API_URL}/auth/login/access-token", data={
        "username": "user@example.com",
        "password": "user123"
    })
    
    if response.status_code != 200:
        print("User not found, registering...")
        response = requests.post(f"{API_URL}/auth/register", json={
            "email": "user@example.com",
            "username": "normaluser",
            "password": "user123"
        })
        if response.status_code != 200:
            print(f"Registration failed: {response.text}")
            return
        # Login again
        response = requests.post(f"{API_URL}/auth/login/access-token", data={
            "username": "user@example.com",
            "password": "user123"
        })
    
    user_token = response.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}
    print("User logged in.")

    # 4. Check Initial Membership
    print("\n4. Check Initial Membership")
    response = requests.get(f"{API_URL}/membership/me", headers=user_headers)
    print(f"Current Membership: {response.json()}")

    # 5. Redeem Code
    print("\n5. Redeem Code")
    response = requests.post(f"{API_URL}/membership/redeem", json={"code": "VIP-2024"}, headers=user_headers)
    if response.status_code == 200:
        print(f"Redemption Successful: {response.json()}")
    else:
        print(f"Redemption Failed: {response.text}")

    # 6. Check Updated Membership
    print("\n6. Check Updated Membership")
    response = requests.get(f"{API_URL}/membership/me", headers=user_headers)
    print(f"Updated Membership: {response.json()}")

if __name__ == "__main__":
    # Run async setup
    asyncio.run(setup_admin())
    
    # Run requests test
    test_membership_flow()
