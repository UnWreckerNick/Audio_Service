import os
from dotenv import load_dotenv

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.database.database import get_database_repo
from app.database.requests import RequestsRepo
from app.models.users import User
from app.schemas.audiofile import TokenSchema
from app.schemas.user import UserSchema, UserCreateSchema

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserService:
    def __init__(self, repo: RequestsRepo):
        self.repo = repo

    async def create_user(self, user: UserCreateSchema):
        await self.repo.users.create_user(user)

    async def get_current_user(self, token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token payload")
        except JWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials")

        user = await self.repo.users.get_by_id(int(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_user(self, user_id: int):
        return await self.repo.users.get_by_id(user_id)

    async def delete_user(self, user: User):
        await self.repo.users.delete(user.id)

    @staticmethod
    async def get_superuser(current_user: UserSchema = Depends(get_current_user)):
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Not enough permission")

    @staticmethod
    async def get_token(sub: dict[str, str]):
        token = jwt.encode(sub, SECRET_KEY, algorithm=ALGORITHM)
        return TokenSchema(access_token=token, token_type="bearer")


def get_user_service(
        repo: RequestsRepo = Depends(get_database_repo)
) -> UserService:
    return UserService(repo=repo)