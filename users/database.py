from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine,async_sessionmaker


DATABASE_URL="sqlite+aiosqlite:///./usuarios.db"
engine=create_async_engine(DATABASE_URL, connect_args={"check_same_thread":False})

AsyncLocalSession=async_sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=AsyncSession, expire_on_commit=False)

Base=declarative_base()

async def get_session():
    async with  AsyncLocalSession() as session:
        yield session








        