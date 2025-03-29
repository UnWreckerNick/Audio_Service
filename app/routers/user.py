import os
import httpx
from dotenv import load_dotenv

from fastapi import APIRouter
from fastapi.params import Depends
from starlette.responses import RedirectResponse

from app.schemas.audiofile import TokenSchema
from app.schemas.user import UserCreateSchema, UserSchema
from app.services.users import UserService, get_user_service, get_current_user_dependency

load_dotenv()

YANDEX_CLIENT_ID = os.getenv("YANDEX_CLIENT_ID")
YANDEX_CLIENT_SECRET = os.getenv("YANDEX_CLIENT_SECRET")

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/login/yandex")
async def login():
    return RedirectResponse(f"https://oauth.yandex.ru/authorize?response_type=code&client_id={YANDEX_CLIENT_ID}")


@router.get("/auth/yandex/callback")
async def yandex_callback(code: str, service: UserService = Depends(get_user_service)):
    # Get Yandex token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth.yandex.ru/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": YANDEX_CLIENT_ID,
                "client_secret": YANDEX_CLIENT_SECRET
            }
        )
        token_data = response.json()

    # Get user info
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            "https://login.yandex.ru/info",
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        user_info = user_response.json()

    user = await service.get_current_user()
    if not user:
        await service.create_user(UserCreateSchema(yandex_id=user_info["id"], email=user_info["default_email"]))

    token = await service.get_token({"sub": str(user.id)})
    return token


@router.post("/token/refresh", response_model=TokenSchema)
async def refresh_token(
        user: UserSchema = Depends(get_current_user_dependency),
        service: UserService = Depends(get_user_service)
):
    token = await service.get_token({"sub": str(user.id)})
    return token
