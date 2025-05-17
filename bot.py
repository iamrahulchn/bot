import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 7473008936))  # Default to your ID if not set

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

REQUIRED_CHANNELS = ["stockode_learning", "stockode.official"]


def join_channels_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    for channel in REQUIRED_CHANNELS:
        keyboard.add(InlineKeyboardButton(f"✅ Join @{channel}", url=f"https://t.me/{channel}"))
    keyboard.add(InlineKeyboardButton("✔️ Done Subscribed! Click ✅Check", callback_data="check_subscriptions"))
    return keyboard


def main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("💰 Balance", callback_data="balance"),
        InlineKeyboardButton("🤝 Referrals", callback_data="referrals"),
        InlineKeyboardButton("🎁 Bonus", callback_data="bonus"),
        InlineKeyboardButton("💸 Withdraw", callback_data="withdraw"),
        InlineKeyboardButton("👛 Set Wallet", callback_data="set_wallet"),
        InlineKeyboardButton("🛠 Support", callback_data="support")
    )
    return keyboard


async def is_user_subscribed(user_id: int):
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=f"@{channel}", user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except:
            return False
    return True


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    await message.answer(
        "👋 *Welcome to stockodetrading Referral Bot!*\n\n"
        "✔️ Refer and Earn Cash!",
        parse_mode="Markdown"
    )

    if await is_user_subscribed(user_id):
        await message.answer("🎉 You're already subscribed! Here's your dashboard:", reply_markup=main_menu_keyboard())
    else:
        await message.answer(
            "🛡️ *Subscribe Channels if you want to start the bot and earn from it:*\n\n"
            "✅ @stockode_learning\n"
            "✅ @stockode.official",
            parse_mode="Markdown",
            reply_markup=join_channels_keyboard()
        )


@dp.callback_query_handler(lambda c: c.data == 'check_subscriptions')
async def check_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if await is_user_subscribed(user_id):
        await bot.answer_callback_query(callback_query.id, "✅ Subscribed successfully!")
        await bot.send_message(user_id, "🎉 You're now verified! Here's your dashboard:", reply_markup=main_menu_keyboard())
    else:
        await bot.answer_callback_query(callback_query.id, "❌ You're not subscribed to all required channels.")
        await bot.send_message(user_id, "❗ Please join *all* channels first:", parse_mode="Markdown", reply_markup=join_channels_keyboard())


@dp.callback_query_handler()
async def menu_buttons(callback_query: types.CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id

    if data == "balance":
        await bot.send_message(user_id, "💰 Your balance: ₹0")

    elif data == "referrals":
        link = f"https://t.me/earningtotrade_bot?start={user_id}"
        await bot.send_message(
            user_id,
            f"➡️ *Total invites:* 0\n"
            f"🚥 *Per Referral:* ₹25\n"
            f"🔗 *Your referral link:* {link}",
            parse_mode="Markdown"
        )

    elif data == "bonus":
        await bot.send_message(user_id, "🎁 Bonus feature coming soon!")

    elif data == "withdraw":
        await bot.send_message(user_id, "💸 Minimum withdrawal is ₹500. Withdrawal panel coming soon!")

    elif data == "set_wallet":
        await bot.send_message(user_id, "👛 Please reply with your wallet UPI ID to set it.")

    elif data == "support":
        await bot.send_message(user_id, "🛠 Contact @stockode_support for help.")


async def main():
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
