import asyncio, logging, json
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

with open('config.json') as f:
    data = json.load(f)
    token = data['token']

from handlers import start, echo

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    bot = Bot(token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(start.router)
    dp.include_router(echo.router)

    try:
        logger.info("Bot starting...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())