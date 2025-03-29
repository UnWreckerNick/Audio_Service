import os
from functools import lru_cache

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.database.requests import RequestsRepo


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session

@lru_cache
def get_database_repo(session: AsyncSession = Depends(get_db)) -> RequestsRepo:
    return RequestsRepo(session=session)