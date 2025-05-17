import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import exceptions
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Channels users must join before using the bot (username without @)
REQUIRED_CHANNELS = ["stockode_learning", "stockode.official"]


def welcome_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("▶️ Start", callback_data="start_bot"))
    return keyboard


def subscribe_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    # Join buttons for each channel
    for ch in REQUIRED_CHANNELS:
        keyboard.add(InlineKeyboardButton(f"➡️ Join @{ch}", url=f"https://t.me/{ch}"))
    # Check subscription button
    keyboard.add(InlineKeyboardButton("✅ Check", callback_data="check_subscriptions"))
    return keyboard


def main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("💰 Balance", callback_data="balance"),
        InlineKeyboardButton("🤝 Referrals", callback_data="referrals"),
        InlineKeyboardButton("🎁 Bonus", callback_data="bonus"),
        InlineKeyboardButton("💸 Withdraw", callback_data="withdraw"),
        InlineKeyboardButton("👛 Set Wallet", callback_data="set_wallet"),
        InlineKeyboardButton("🛠 Support", callback_data="support"),
    )
    return keyboard


async def is_user_subscribed(user_id: int):
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=f"@{channel}", user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except exceptions.TelegramBadRequest:
            return False
    return True


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    welcome_text = (
        "🤖 *What can this bot do?*\n\n"
        "Welcome to *stockodetrading Referral Bot*\n\n"
        "✔️ Refer and Earn Cash\n\n"
        "Press ▶️ Start to continue."
    )
    await message.answer(welcome_text, reply_markup=welcome_keyboard(), parse_mode="Markdown")


@dp.callback_query_handler(lambda c: c.data == "start_bot")
async def start_bot(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    prompt_text = (
        "🛡️ *Subscribe Channels if you want to start the bot and earn from it*\n\n"
        + "\n".join(f"✅ @{ch}" for ch in REQUIRED_CHANNELS)
        + "\n\n✔️ Done subscribed? Click ✅ Check"
    )
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(user_id, prompt_text, reply_markup=subscribe_keyboard(), parse_mode="Markdown")


@dp.callback_query_handler(lambda c: c.data == "check_subscriptions")
async def check_subscriptions(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if await is_user_subscribed(user_id):
        await bot.answer_callback_query(callback_query.id, "✅ Subscription verified!")
        await bot.send_message(
            user_id,
            "🎉 Thanks for subscribing! Here's your main menu:",
            reply_markup=main_menu_keyboard(),
        )
    else:
        await bot.answer_callback_query(callback_query.id, "❌ You are not subscribed to all required channels.")
        await bot.send_message(
            user_id,
            "⚠️ You *must* join all channels to start using the bot.\n\n"
            "Please join and then press ✅ Check again.",
            reply_markup=subscribe_keyboard(),
            parse_mode="Markdown"
        )


@dp.callback_query_handler()
async def handle_buttons(callback_query: types.CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id
    await bot.answer_callback_query(callback_query.id)

    if data == "balance":
        await bot.send_message(user_id, "💰 Your balance is: ₹0")  # Placeholder
    elif data == "referrals":
        await bot.send_message(user_id, "🤝 You have 0 referrals.")  # Placeholder
    elif data == "bonus":
        await bot.send_message(user_id, "🎁 No bonus available yet.")  # Placeholder
    elif data == "withdraw":
        await bot.send_message(user_id, "💸 Withdrawals are allowed for minimum ₹500.")  # Placeholder
    elif data == "set_wallet":
        await bot.send_message(user_id, "👛 Please send your wallet address.")  # Placeholder
    elif data == "support":
        await bot.send_message(user_id, "🛠 Support will respond soon!")  # Placeholder


async def main():
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
