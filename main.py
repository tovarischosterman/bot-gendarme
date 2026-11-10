import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers.start import router as start_router
from handlers.rest import router as rest_router
from handlers.appeals import router as appeals_router
from handlers.admin_replies import router as admin_replies_router
from handlers.events import router as events_router

from database.db import init_db


dp = Dispatcher()
dp.include_router(start_router)
dp.include_router(appeals_router)
dp.include_router(admin_replies_router)
dp.include_router(rest_router)
dp.include_router(events_router)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    await init_db()

    async with Bot(token=BOT_TOKEN) as bot:
        me = await bot.get_me()

        logging.info("Бот запущен: @%s", me.username)

        await bot.delete_webhook(drop_pending_updates=True)

        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
