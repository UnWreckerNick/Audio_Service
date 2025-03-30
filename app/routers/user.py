import os
import secrets

import httpx
from dotenv import load_dotenv

from fastapi import APIRouter, Request, HTTPException
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
async def login_yandex(request: Request):
    try:
        # Генерируем state
        state = secrets.token_urlsafe(16)

        # Проверяем сессию
        if not hasattr(request, 'session'):
            raise HTTPException(status_code=500, detail="Session middleware not configured")
        request.session["oauth_state"] = state

        # Генерируем redirect_uri
        redirect_uri = request.url_for("yandex_callback")

        # Формируем URL для Яндекса
        url = (
            f"https://oauth.yandex.ru/authorize?"
            f"response_type=code&"
            f"client_id={YANDEX_CLIENT_ID}&"
            f"redirect_uri={redirect_uri}&"
            f"state={state}"
        )

        return RedirectResponse(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/auth/yandex/callback")
async def yandex_callback(
        request: Request,
        code: str,
        state: str,
        service: UserService = Depends(get_user_service)
):
    # Проверяем state для защиты от CSRF
    if state != request.session.get("oauth_state"):
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    # Получаем Yandex token
    redirect_uri = request.url_for("yandex_callback")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth.yandex.ru/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": YANDEX_CLIENT_ID,
                "client_secret": YANDEX_CLIENT_SECRET,
                "redirect_uri": redirect_uri
            }
        )
        token_data = response.json()

    if "error" in token_data:
        raise HTTPException(
            status_code=400,
            detail=f"Yandex OAuth error: {token_data.get('error_description', token_data['error'])}"
        )

    # Получаем информацию о пользователе
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            "https://login.yandex.ru/info",
            headers={"Authorization": f"OAuth {token_data['access_token']}"}
        )
        user_info = user_response.json()

    # Ищем пользователя по yandex_id или создаем нового
    user = await service.repo.users.get_user_by_yandex_id(user_info["id"])
    if not user:
        user = await service.create_user(
            UserCreateSchema(
                yandex_id=user_info["id"],
                email=user_info["default_email"]
            )
        )

    # Создаем внутренний токен API
    token = await service.get_token({"sub": str(user.yandex_id)})

    # Возвращаем токен (можно перенаправить на фронтенд с токеном в URL)
    return token


@router.post("/token/refresh", response_model=TokenSchema)
async def refresh_token(
        user: UserSchema = Depends(get_current_user_dependency),
        service: UserService = Depends(get_user_service)
):
    token = await service.get_token({"sub": str(user.yandex_id)})
    return token
