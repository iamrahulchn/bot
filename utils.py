from aiogram import Bot, types
import os

CHANNELS = os.getenv("CHANNELS").split(",")

async def check_subscribed(user_id: int, bot: Bot):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except:
            return False
    return True
