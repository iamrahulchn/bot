import os
import asyncio
from aiogram import Bot, Dispatcher
from handlers import register_handlers
from dotenv import load_dotenv
from aiohttp import web

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))  # <-- Here we get PORT from env or default 8000

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
register_handlers(dp)

async def handle(request):
    return web.Response(text="Bot is running!")

async def start_bot():
    await dp.start_polling(bot)

async def main():
    app = web.Application()
    app.router.add_get('/', handle)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

    await start_bot()

if __name__ == "__main__":
    asyncio.run(main())
