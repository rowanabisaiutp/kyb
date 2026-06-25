
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

connect_args = {}
if (
    "flycast" in settings.async_database_url
    or "internal" in settings.async_database_url
):
    connect_args["ssl"] = False

engine = create_async_engine(
    settings.async_database_url,
    echo=settings.APP_ENV == "development",
    connect_args=connect_args,
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
