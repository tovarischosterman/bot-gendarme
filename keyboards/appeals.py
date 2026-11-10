
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_appeal_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="В главное меню",
                    callback_data="appeal:exit"
                )
            ]
        ]
    )
