import os
from datetime import datetime, timedelta, UTC

from dotenv import load_dotenv

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.database.database import get_database_repo
from app.database.requests import RequestsRepo
from app.schemas.audiofile import TokenSchema
from app.schemas.user import UserSchema, UserCreateSchema

load_dotenv()

YANDEX_SECRET_KEY = os.getenv("YANDEX_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserService:
    def __init__(self, repo: RequestsRepo):
        self.repo = repo

    async def create_user(self, user: UserCreateSchema):
        await self.repo.users.create_user(user)

    async def get_current_user(self, token: str):
        try:
            payload = jwt.decode(token, YANDEX_SECRET_KEY, algorithms=[ALGORITHM])
            yandex_id: str = payload.get("sub")
            if not yandex_id:
                raise HTTPException(status_code=401, detail="Invalid token payload")
        except JWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials")

        user = await self.repo.users.get_user_by_yandex_id(yandex_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_user(self, user_id: int):
        return await self.repo.users.get_by_id(user_id)

    async def delete_user(self, user_id: int):
        await self.repo.users.delete(user_id)

    async def update_user(self, user_id: int, user_data: dict):
        return await self.repo.users.update(user_id, **user_data)

    @staticmethod
    async def get_token(sub: dict[str, str]):
        to_encode = sub.copy()
        expire = datetime.now(UTC)+ timedelta(minutes=30)
        to_encode.update({"exp": int(expire.timestamp())})  # noqa
        token = jwt.encode(to_encode, YANDEX_SECRET_KEY, algorithm=ALGORITHM)
        return TokenSchema(access_token=token, token_type="bearer")


def get_user_service(
        repo: RequestsRepo = Depends(get_database_repo)
) -> UserService:
    return UserService(repo=repo)


async def get_current_user_dependency(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.get_current_user(token)

async def get_superuser_dependency(
    current_user: UserSchema = Depends(get_current_user_dependency)
) -> UserSchema:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permission")
    return current_user
