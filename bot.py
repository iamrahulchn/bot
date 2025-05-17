import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand, BotCommandScopeDefault
from dotenv import load_dotenv
import os

from handlers import register_handlers

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

async def main():
    await bot.set_my_commands([
        BotCommand(command="start", description="Start the bot"),
    ], scope=BotCommandScopeDefault())

    register_handlers(dp, bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
