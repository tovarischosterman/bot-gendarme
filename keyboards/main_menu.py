from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Прислать анкету",
                    callback_data="menu:dossier"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Связаться с администрацией",
                    callback_data="menu:contact"
                ),
                InlineKeyboardButton(
                    text="Предложить идею",
                    callback_data="menu:idea"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Ивенты",
                    callback_data="menu:events"
                ),
                InlineKeyboardButton(
                    text="Взять рест",
                    callback_data="menu:rest"
                )
            ]
        ]
    )
