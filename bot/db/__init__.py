import os
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

ENGINE: AsyncEngine


def init_engine():
    if db_uri := os.environ.get("DB_URI"):
        global ENGINE
        ENGINE = create_async_engine(db_uri)
    else:
        raise EnvironmentError("Environment variable not found: DB_URI")


async def close():
    global ENGINE
    await ENGINE.dispose()


def async_session() -> AsyncSession:
    global ENGINE
    return AsyncSession(ENGINE)
