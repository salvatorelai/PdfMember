from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.crud.base import CRUDBase
from app.models.system import SystemSetting
from app.schemas.system import SystemSettingCreate, SystemSettingUpdate

class CRUDSystemSetting(CRUDBase[SystemSetting, SystemSettingCreate, SystemSettingUpdate]):
    async def get(self, db: AsyncSession, id: Any) -> Optional[SystemSetting]:
        # Override get to use key instead of id, since SystemSetting uses key as PK
        result = await db.execute(select(SystemSetting).filter(SystemSetting.key == id))
        return result.scalars().first()
        
    async def create_or_update(self, db: AsyncSession, obj_in: SystemSettingCreate) -> SystemSetting:
        db_obj = await self.get(db, obj_in.key)
        if db_obj:
            return await self.update(db, db_obj=db_obj, obj_in=obj_in)
        return await self.create(db, obj_in=obj_in)

system_setting = CRUDSystemSetting(SystemSetting)
