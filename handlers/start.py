from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile

from config import BASE_DIR
from keyboards.main_menu import get_main_menu


router = Router()

WELCOME_IMAGE = BASE_DIR / "assets" / "welcome.jpg"


@router.message(CommandStart())
async def start_handler(message: Message):
    photo = FSInputFile(WELCOME_IMAGE)

    await message.answer_photo(
        photo=photo,
        caption=(
            "<b>Вы находитесь в меню.</b> \n\n"
            "При возникновении проблем свяжитесь с владельцем @TovarischOsterman. \n"
            "Раздел \"Ивенты\" временно не работает."
        ),
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
