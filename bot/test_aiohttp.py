import asyncio
import aiohttp

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.telegram.org") as r:
            print(r.status)
            print(await r.text())

asyncio.run(main())