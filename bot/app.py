"""Точка входа Telegram-бота AI NAVI."""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from database import init_db
from handlers import router
from session import ProxyAwareAiohttpSession
from singleton import SingleInstanceLock, stop_running_instance

logger = logging.getLogger(__name__)


def validate_bot_token(token: str) -> None:
    """Проверяет наличие токена и завершает работу при его отсутствии."""
    if token:
        return

    logger.error(
        "Переменная окружения BOT_TOKEN не задана. "
        "Создайте файл .env на основе .env.example и укажите токен бота.",
    )
    sys.exit(1)


async def main() -> None:
    """Запускает бота и обрабатывает входящие обновления."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    if "--force" in sys.argv:
        logger.info("Принудительный перезапуск: остановка старых экземпляров...")
        stop_running_instance()

    instance_lock = SingleInstanceLock()
    instance_lock.acquire()

    config = Config()
    validate_bot_token(config.bot_token)

    if config.admin_ids:
        logger.info("Администраторы: %s", ", ".join(map(str, sorted(config.admin_ids))))
    else:
        logger.warning("ADMIN_ID не задан — админ-меню отключено")

    init_db()

    session = ProxyAwareAiohttpSession()
    bot = Bot(token=config.bot_token, session=session)
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(router)

    logger.info("========================")
    logger.info("AI NAVI Bot started")
    logger.info("========================")

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()
        instance_lock.release()


if __name__ == "__main__":
    asyncio.run(main())
