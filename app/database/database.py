import asyncio
import os
from functools import lru_cache

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.database.requests import RequestsRepo
from app.models.base import Base
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SYSTEM_DATABASE_URL = os.getenv("SYSTEM_DATABASE_URL")

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

async def wait_for_db(wait_engine, retries=20, delay=5):
    for attempt in range(retries):
        try:
            async with wait_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1}/{retries} failed: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
    raise Exception("Database is not available after retries")

async def init_db():
    # Ожидаем доступности базы postgres
    system_engine = create_async_engine(SYSTEM_DATABASE_URL, echo=True)
    await wait_for_db(system_engine)

    # Создаём базу audio_db, если её нет
    async with system_engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname='audio_db'")
        )
        if not result.scalar():
            await conn.execute(text("CREATE DATABASE audio_db"))
    await system_engine.dispose()

    # Ожидаем доступности audio_db и создаём таблицы
    await wait_for_db(engine)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with async_session() as session:
        yield session

@lru_cache
def get_database_repo(session: AsyncSession = Depends(get_db)) -> RequestsRepo:
    return RequestsRepo(session=session)