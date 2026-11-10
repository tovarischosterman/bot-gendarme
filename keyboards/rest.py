from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_rest_confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Подтвердить",
                    callback_data="rest:confirm"
                ),
                InlineKeyboardButton(
                    text="Внести изменения",
                    callback_data="rest:edit"
                )
            ]
        ]
    )


def get_existing_rest_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Изменить дату окончания",
                    callback_data="rest:change_end"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Завершить рест",
                    callback_data="rest:finish"
                )
            ]
        ]
    )
