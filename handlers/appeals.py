
import logging

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError
from keyboards.appeals import get_appeal_menu
from keyboards.main_menu import get_main_menu

from config import (
    ADMIN_CHAT_ID,
    DOSSIER_THREAD_ID,
    IDEA_THREAD_ID,
    CONTACT_THREAD_ID
)

from states.appeals import AppealStates
from database.queries import create_appeal


router = Router()
logger = logging.getLogger(__name__)


APPEAL_CATEGORIES = {
    "menu:dossier": {
        "name": "dossier",
        "title": "Прислать анкету",
        "thread_id": DOSSIER_THREAD_ID
    },
    "menu:idea": {
        "name": "idea",
        "title": "Предложить идею",
        "thread_id": IDEA_THREAD_ID
    },
    "menu:contact": {
        "name": "contact",
        "title": "Связаться с администрацией",
        "thread_id": CONTACT_THREAD_ID
    }
}



@router.callback_query(F.data.in_(APPEAL_CATEGORIES))
async def start_appeal(
    callback: CallbackQuery,
    state: FSMContext
):
    """Выбирает категорию обращения."""

    category = APPEAL_CATEGORIES[callback.data]

    await state.update_data(
        category=category["name"],
        thread_id=category["thread_id"]
    )

    await state.set_state(AppealStates.waiting_for_message)

    await callback.message.edit_caption(
        caption=(
            f"<b>Раздел: {category['title']}</b>\n\n"
            "Все сообщения будут направлены в выбранную тему.\n\n"
        ),
        reply_markup=get_appeal_menu(),
        parse_mode="HTML"
    )

    await callback.answer()



@router.message(AppealStates.waiting_for_message)
async def receive_appeal(
    message: Message,
    state: FSMContext,
    bot: Bot
):
    """Принимает и пересылает обращение администрации."""

    if not ADMIN_CHAT_ID:
        logger.error("ADMIN_CHAT_ID не настроен")
        await state.clear()
        return

    data = await state.get_data()

    category = data["category"]
    thread_id = data["thread_id"]

    try:
        forwarded = await bot.forward_message(
            chat_id=ADMIN_CHAT_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
            message_thread_id=thread_id
        )

        await create_appeal(
            user_id=message.from_user.id,
            admin_message_id=forwarded.message_id,
            admin_chat_id=ADMIN_CHAT_ID,
            category=category
        )

    except TelegramAPIError:
        logger.exception(
            "Не удалось переслать обращение пользователя %s",
            message.from_user.id
        )

    except Exception:
        logger.exception(
            "Ошибка при сохранении обращения пользователя %s",
            message.from_user.id
        )


@router.callback_query(F.data == "appeal:exit")
async def exit_appeals(
    callback: CallbackQuery,
    state: FSMContext
):
    """Завершает режим обращений."""

    await state.clear()

    await callback.message.edit_caption(
        caption="<b>Главное меню</b>",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

    await callback.answer()
