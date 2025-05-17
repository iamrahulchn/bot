from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

async def main():
    print("✅ Aiogram is working!")
    # Start polling or extend later

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
