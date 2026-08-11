from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

def prepare_async_db_url(url_str: str) -> tuple[str, dict]:
    url_str = url_str.strip()
    connect_args = {}

    if not url_str or "sqlite" in url_str:
        return url_str, {"check_same_thread": False}

    try:
        parsed = urlparse(url_str)
        scheme = parsed.scheme

        # Convert postgres:// or postgresql:// to postgresql+asyncpg://
        if scheme in ("postgres", "postgresql"):
            scheme = "postgresql+asyncpg"

        # Filter out unsupported asyncpg query params (e.g. channel_binding, sslmode, etc.)
        qs = parse_qs(parsed.query)
        allowed_qs = {}
        for k, v in qs.items():
            if k.lower() in ("ssl", "timeout", "command_timeout"):
                allowed_qs[k] = v

        new_query = urlencode(allowed_qs, doseq=True)
        cleaned_url = urlunparse((scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))

        # Default remote PostgreSQL (Neon/Supabase/Render) to SSL
        if "localhost" not in parsed.netloc and "127.0.0.1" not in parsed.netloc:
            connect_args["ssl"] = True

        return cleaned_url, connect_args
    except Exception as e:
        print("Database URL parse warning:", e)
        return url_str, connect_args

db_url, connect_args = prepare_async_db_url(settings.DATABASE_URL)

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
