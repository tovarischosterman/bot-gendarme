from html import escape
from datetime import datetime
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from config import ADMIN_CHAT_ID, RESTS_THREAD_ID
from database.queries import (
    get_active_rests,
    finish_expired_rests,
    get_setting,
    set_setting
)


logger = logging.getLogger(__name__)

MESSAGE_KEY = "rests_message_id"


def format_rest(rest) -> str:
    """Формирует строку с информацией об одном ресте."""

    if rest["username"]:
        name = f"@{escape(rest['username'])}"
    else:
        name = escape(rest["first_name"] or "Пользователь")

    start_date = datetime.strptime(
        rest["start_date"], "%Y-%m-%d"
    ).strftime("%d.%m.%Y")

    end_date = datetime.strptime(
        rest["end_date"], "%Y-%m-%d"
    ).strftime("%d.%m.%Y")

    return (
        f"• <b>{name}</b> — {start_date} — {end_date}"
    )


async def update_rest_publication(bot: Bot):
    """Обновляет публикацию со списком активных рестов."""

    if not ADMIN_CHAT_ID:
        logger.error("ADMIN_CHAT_ID не настроен")
        return

    await finish_expired_rests()

    rests = await get_active_rests()

    if rests:
        rest_list = "\n".join(
            format_rest(rest) for rest in rests
        )

        text = (
            "<b>Ресты</b>\n\n"
            f"{rest_list}\n\n"
        )
    else:
        text = (
            "<b>Ресты</b>\n\n"
            "Сейчас никто не находится в ресте."
        )

    message_id = await get_setting(MESSAGE_KEY)

    if message_id:
        try:
            await bot.edit_message_text(
                chat_id=ADMIN_CHAT_ID,
                message_id=int(message_id),
                text=text,
                parse_mode="HTML"
            )

            return

        except TelegramBadRequest as error:
            if "message is not modified" in str(error).lower():
                return

            logger.warning(
                "Не удалось отредактировать список рестов: %s",
                error
            )

        except TelegramForbiddenError as error:
            logger.warning(
                "Нет доступа к редактированию сообщения: %s",
                error
            )

        try:
            await bot.delete_message(
                chat_id=ADMIN_CHAT_ID,
                message_id=int(message_id)
            )
        except (TelegramBadRequest, TelegramForbiddenError) as error:
            logger.warning(
                "Не удалось удалить старую публикацию рестов: %s",
                error
            )

    message = await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        message_thread_id=RESTS_THREAD_ID,
        text=text,
        parse_mode="HTML"
    )

    await set_setting(MESSAGE_KEY, str(message.message_id))
