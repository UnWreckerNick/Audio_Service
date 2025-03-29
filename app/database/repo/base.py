from typing import Any, Optional, Type, TypeVar

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

T = TypeVar('T', bound=DeclarativeMeta)


class BaseRepo:
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get_by_id(self, obj_id: Any) -> Optional[T]:
        stmt = (
            select(self.model)
            .filter_by(id=obj_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, obj_id: Any | list[Any]) -> list[T] | None:
        if isinstance(obj_id, list):
            stmt = (
                delete(self.model)
                .filter(self.model.id.in_(obj_id))
                .returning(self.model)
            )
        else:
            stmt = (
                delete(self.model)
                .filter_by(id=obj_id)
                .returning(self.model)
            )

        result = await self.session.execute(stmt)
        await self.session.commit()

        if isinstance(obj_id, list):
            return list(result.scalars().all())
        else:
            return result.scalar_one_or_none()

    async def update(self, obj_id: Any | list[Any], **kwargs) -> T | list[T] | None:
        if not obj_id:
            return None

        if isinstance(obj_id, list):
            stmt = (
                update(self.model)
                .values(**kwargs)
                .where(self.model.id.in_(obj_id))
                .execution_options(synchronize_session="fetch")
                .returning(self.model)
            )
        else:
            stmt = (
                update(self.model)
                .values(**kwargs)
                .filter_by(id=obj_id)
                .returning(self.model)
            )
        result = await self.session.execute(stmt)
        await self.session.commit()

        if isinstance(obj_id, list):
            return list(result.scalars().all())

        return result.scalar_one_or_none()