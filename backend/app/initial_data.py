import asyncio
import logging

from app.db.session import SessionLocal
from app import crud, schemas
from app.models.user import UserRole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db() -> None:
    async with SessionLocal() as db:
        user = await crud.user.get_by_email(db, email="admin@example.com")
        if not user:
            logger.info("Creating admin user...")
            user_in = schemas.UserCreate(
                email="admin@example.com",
                password="admin123",
                username="admin",
                role=UserRole.ADMIN
            )
            user = await crud.user.create(db, obj_in=user_in)
            logger.info(f"Admin user created: {user.email}")
        else:
            logger.info("Admin user already exists")

async def main() -> None:
    logger.info("Creating initial data")
    await init_db()
    logger.info("Initial data created")

if __name__ == "__main__":
    asyncio.run(main())
