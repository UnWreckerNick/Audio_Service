from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.database.repo.base import BaseRepo
from app.schemas.user import UserCreateSchema


class UserRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)  # noqa

    async def create_user(self, user: UserCreateSchema) -> User:
        new_user = User(**user.model_dump())
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

    async def get_user_by_yandex_id(self, yandex_id: str):
        stmt = select(User).where(User.yandex_id == yandex_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()