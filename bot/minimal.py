import asyncio
import os

from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN", "")


async def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN не задан")

    bot = Bot(TOKEN)

    try:
        me = await bot.get_me()
        print("SUCCESS")
        print(me)
    finally:
        await bot.session.close()


asyncio.run(main())
