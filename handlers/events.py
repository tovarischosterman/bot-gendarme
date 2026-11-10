from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(F.data == "menu:events")
async def events_handler(callback: CallbackQuery):
    await callback.answer(
        "Этот раздел пока не работает.",
        show_alert=True
    )