from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.database import database
from app.routers.user import router as user_router
from app.routers.audiofile import router as audio_router
from app.routers.superuser import router as superuser_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa
    async with database.engine.begin():
        yield

app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(audio_router)
app.include_router(superuser_router)
