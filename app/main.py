import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.database import database
from app.routes.user import router as user_router
from app.routes.audiofile import router as audio_router
from app.routes.superuser import router as superuser_router


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa
    await database.init_db()
    async with database.engine.begin():
        yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY) # noqa

app.include_router(user_router)
app.include_router(audio_router)
app.include_router(superuser_router)
