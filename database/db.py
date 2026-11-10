from contextlib import asynccontextmanager

import aiosqlite

from config import DATABASE_PATH
from database.models import (
    RESTS_TABLE,
    RESTS_INDEX,
    BOT_SETTINGS_TABLE,
    APPEALS_TABLE,
    APPEALS_USER_INDEX
)


async def init_db():
    """Создаёт базу данных и необходимые таблицы."""

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(RESTS_TABLE)
        await db.execute(RESTS_INDEX)
        await db.execute(BOT_SETTINGS_TABLE)
        await db.execute(APPEALS_TABLE)
        await db.execute(APPEALS_USER_INDEX)

        await db.commit()


@asynccontextmanager
async def get_db():
    """Открывает подключение к SQLite и закрывает его после работы."""

    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db
