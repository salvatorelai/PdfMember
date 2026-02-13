import asyncio
from app.db.session import SessionLocal
from app.crud import user
from app.models.user import UserRole
from app.core.config import settings

async def promote_user():
    async with SessionLocal() as db:
        u = await user.get_by_username(db, username="testuser")
        if u:
            print(f"Found user: {u.username}, Role: {u.role}")
            u.role = UserRole.SUPER_ADMIN
            db.add(u)
            await db.commit()
            print(f"Promoted {u.username} to SUPER_ADMIN")
        else:
            print("User not found")

if __name__ == "__main__":
    asyncio.run(promote_user())
