from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

db_url = settings.DATABASE_URL.strip()

# Convert postgres:// or postgresql:// to postgresql+asyncpg:// for Neon / Supabase / Render
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

connect_args = {}

# Fix asyncpg keyword argument compatibility for Neon/Supabase (sslmode -> ssl)
if "asyncpg" in db_url:
    if "sslmode=" in db_url:
        db_url = db_url.replace("sslmode=require", "ssl=require") \
                       .replace("sslmode=prefer", "ssl=require") \
                       .replace("sslmode=verify-ca", "ssl=require") \
                       .replace("sslmode=verify-full", "ssl=require")
    # If no ssl parameter in URL for remote PostgreSQL, default to ssl=True
    if "ssl=" not in db_url and "localhost" not in db_url and "127.0.0.1" not in db_url:
        connect_args["ssl"] = True

elif "sqlite" in db_url:
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    db_url,
    echo=settings.DEBUG,
    connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
