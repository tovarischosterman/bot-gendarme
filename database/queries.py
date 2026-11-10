from datetime import datetime

from database.db import get_db


async def create_rest(
    user_id: int,
    username: str | None,
    first_name: str,
    start_date: str,
    end_date: str
):
    """Создаёт новый рест."""

    now = datetime.now().isoformat()

    async with get_db() as db:
        await db.execute(
            """
            INSERT INTO rests (
                user_id,
                username,
                first_name,
                start_date,
                end_date,
                is_active,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (
                user_id,
                username,
                first_name,
                start_date,
                end_date,
                now,
                now
            )
        )

        await db.commit()


async def get_user_rest(user_id: int):
    """Возвращает активный рест пользователя."""

    async with get_db() as db:
        cursor = await db.execute(
            """
            SELECT *
            FROM rests
            WHERE user_id = ? AND is_active = 1
            """,
            (user_id,)
        )

        return await cursor.fetchone()


async def extend_rest(user_id: int, new_end_date: str):
    """Изменяет дату окончания существующего реста."""

    now = datetime.now().isoformat()

    async with get_db() as db:
        await db.execute(
            """
            UPDATE rests
            SET end_date = ?,
                reminded_for_end_date = NULL,
                updated_at = ?
            WHERE user_id = ? AND is_active = 1
            """,
            (new_end_date, now, user_id)
        )

        await db.commit()


async def get_active_rests():
    """Возвращает все активные ресты."""

    async with get_db() as db:
        cursor = await db.execute(
            """
            SELECT *
            FROM rests
            WHERE is_active = 1
            ORDER BY id ASC
            """
        )

        return await cursor.fetchall()


async def finish_expired_rests():
    """Завершает ресты, которые закончились."""

    today = datetime.now().strftime("%Y-%m-%d")

    async with get_db() as db:
        await db.execute(
            """
            UPDATE rests
            SET is_active = 0,
                updated_at = ?
            WHERE end_date < ? AND is_active = 1
            """,
            (datetime.now().isoformat(), today)
        )

        await db.commit()


async def update_user_info(
    user_id: int,
    username: str | None,
    first_name: str
):
    """Обновляет username и имя пользователя."""

    now = datetime.now().isoformat()

    async with get_db() as db:
        await db.execute(
            """
            UPDATE rests
            SET username = ?,
                first_name = ?,
                updated_at = ?
            WHERE user_id = ? AND is_active = 1
            """,
            (username, first_name, now, user_id)
        )

        await db.commit()


async def get_setting(key: str):
    """Получает значение настройки бота."""

    async with get_db() as db:
        cursor = await db.execute(
            "SELECT value FROM bot_settings WHERE key = ?",
            (key,)
        )

        row = await cursor.fetchone()
        return row["value"] if row else None


async def set_setting(key: str, value: str):
    """Создаёт или обновляет настройку бота."""

    async with get_db() as db:
        await db.execute(
            """
            INSERT INTO bot_settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value)
        )

        await db.commit()

async def finish_user_rest(user_id: int):
    """Досрочно завершает активный рест пользователя."""

    now = datetime.now().isoformat()

    async with get_db() as db:
        await db.execute(
            """
            UPDATE rests
            SET is_active = 0,
                updated_at = ?
            WHERE user_id = ? AND is_active = 1
            """,
            (now, user_id)
        )

        await db.commit()


async def create_appeal(
    user_id: int,
    admin_message_id: int,
    admin_chat_id: int,
    category: str
):
    """Сохраняет обращение в базе данных."""

    now = datetime.now().isoformat()

    async with get_db() as db:
        await db.execute(
            """
            INSERT INTO appeals (
                user_id,
                admin_message_id,
                admin_chat_id,
                category,
                delivery_status,
                created_at
            )
            VALUES (?, ?, ?, ?, 'received', ?)
            """,
            (
                user_id,
                admin_message_id,
                admin_chat_id,
                category,
                now
            )
        )

        await db.commit()


async def get_appeal(
    admin_message_id: int,
    admin_chat_id: int
):
    """Находит обращение по сообщению в административном чате."""

    async with get_db() as db:
        cursor = await db.execute(
            """
            SELECT *
            FROM appeals
            WHERE admin_message_id = ?
              AND admin_chat_id = ?
            """,
            (admin_message_id, admin_chat_id)
        )

        return await cursor.fetchone()


async def update_appeal_category(
    admin_message_id: int,
    admin_chat_id: int,
    category: str
):
    """Изменяет категорию обращения."""

    async with get_db() as db:
        await db.execute(
            """
            UPDATE appeals
            SET category = ?
            WHERE admin_message_id = ?
              AND admin_chat_id = ?
            """,
            (category, admin_message_id, admin_chat_id)
        )

        await db.commit()


async def update_appeal_status(
    admin_message_id: int,
    admin_chat_id: int,
    status: str
):
    """Изменяет статус доставки ответа."""

    async with get_db() as db:
        await db.execute(
            """
            UPDATE appeals
            SET delivery_status = ?
            WHERE admin_message_id = ?
              AND admin_chat_id = ?
            """,
            (status, admin_message_id, admin_chat_id)
        )

        await db.commit()
