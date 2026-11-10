import logging

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.exceptions import TelegramAPIError

from config import ADMIN_CHAT_ID
from database.queries import (
    get_appeal,
    update_appeal_status
)


router = Router()
logger = logging.getLogger(__name__)


@router.message(
    F.chat.id == ADMIN_CHAT_ID,
    F.reply_to_message
)
async def admin_reply(
    message: Message,
    bot: Bot
):
    """Пересылает ответ администрации автору обращения."""

    # Не обрабатываем команды как обычные ответы.
    if message.text and message.text.startswith("/"):
        return

    original_message = message.reply_to_message

    appeal = await get_appeal(
        admin_message_id=original_message.message_id,
        admin_chat_id=message.chat.id
    )

    # Сообщение не является зарегистрированным обращением.
    if not appeal:
        return

    try:
        await bot.copy_message(
            chat_id=appeal["user_id"],
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )

    except TelegramAPIError:
        logger.exception(
            "Не удалось доставить ответ пользователю %s",
            appeal["user_id"]
        )

        await update_appeal_status(
            original_message.message_id,
            message.chat.id,
            "failed"
        )
        return

    await update_appeal_status(
        original_message.message_id,
        message.chat.id,
        "delivered"
    )
