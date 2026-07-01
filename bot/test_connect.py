import asyncio
import sys

from aiogram import Bot

from config import Config
from session import ProxyAwareAiohttpSession


async def main() -> None:
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    config = Config()
    session = ProxyAwareAiohttpSession()
    bot = Bot(token=config.bot_token, session=session)
    try:
        me = await bot.get_me()
        print(f"OK: @{me.username}")
    finally:
        await bot.session.close()


asyncio.run(main())
