import asyncio
import logging
import json
from pathlib import Path
from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import TelegramObject
from models.database import Database
from typing import Dict, Any, Callable, Awaitable
from handlers import start, echo

BASE_DIR = Path(__file__).parent

class DBModdleware(BaseMiddleware):
    def __init__(self, db: Database):
        self.db = db

    async def __call__(
        self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject, data: Dict[str, Any]) -> Any:
        data['db'] = self.db
        return await handler(event, data)
    

from handlers import start, echo

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    try:
        config_path = BASE_DIR / "config.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        bot_token = config.get('token')
        if not bot_token:
            logger.error("Токена нет")
            return
    except Exception as e:
        logger.error(f"Конфига нет: {e}")
        return

    try:
        db = Database(config['database'])
        db.cursor.execute("SELECT 1")
        if db.cursor.fetchone():
            logger.info("БД подключена")
        else:
            logger.error("Тестовый запрос не долетел до БД")
            return
    except Exception as e:
        logger.error(f"Ошибка подключения к БД: {e}")
        return

    try:
        bot = Bot(token=bot_token)
        dp = Dispatcher(storage=MemoryStorage())

        dp.update.middleware(DBModdleware(db))
        
        dp.include_router(start.router)
        dp.include_router(echo.router)

        logger.info("Старт бота")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка бота: {e}")
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")

if __name__ == "__main__":
    asyncio.run(main())