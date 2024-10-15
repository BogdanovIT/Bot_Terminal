import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers.handlers import router
from database.models import async_main
from aiogram.methods import DeleteWebhook

async def main():
    await async_main()
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)

if __name__ == "__main__":
    #logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is offline")
