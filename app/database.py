import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./recipes.db")

# создать асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    future=True,
    echo=False,
)

# сессии (async)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    future=True,
)


async def get_db():
    """
    FastAPI dependency — возвращает AsyncSession.
    Используйте: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """
    Инициализация БД: создание таблиц.
    Вызывается при старте приложения.
    """
    async with engine.begin() as conn:
        # создаём таблицы на синхронном уровне через run_sync
        await conn.run_sync(Base.metadata.create_all)
