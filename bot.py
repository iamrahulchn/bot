import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram import Router

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 7473008936))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

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


@router.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    await message.answer(
        "👋 *Welcome to stockodetrading Referral Bot!*\n\n"
        "✔️ Refer and Earn Cash!",
        parse_mode=ParseMode.MARKDOWN
    )

    if await is_user_subscribed(user_id):
        await message.answer("🎉 You're already subscribed! Here's your dashboard:", reply_markup=main_menu_keyboard())
    else:
        await message.answer(
            "🛡️ *Subscribe Channels if you want to start the bot and earn from it:*\n\n"
            "✅ @stockode_learning\n"
            "✅ @stockode.official",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=join_channels_keyboard()
        )


@router.callback_query(F.data == "check_subscriptions")
async def check_subscriptions(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if await is_user_subscribed(user_id):
        await callback_query.message.answer("🎉 You're now verified! Here's your dashboard:", reply_markup=main_menu_keyboard())
        await callback_query.answer("✅ Subscribed successfully!")
    else:
        await callback_query.message.answer("❗ Please join *all* channels first:", parse_mode=ParseMode.MARKDOWN, reply_markup=join_channels_keyboard())
        await callback_query.answer("❌ You're not subscribed to all required channels.")


@router.callback_query()
async def handle_buttons(callback_query: types.CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id

    if data == "balance":
        await callback_query.message.answer("💰 Your balance: ₹0")

    elif data == "referrals":
        link = f"https://t.me/earningtotrade_bot?start={user_id}"
        await callback_query.message.answer(
            f"➡️ *Total invites:* 0\n"
            f"🚥 *Per Referral:* ₹25\n"
            f"🔗 *Your referral link:* {link}",
            parse_mode=ParseMode.MARKDOWN
        )

    elif data == "bonus":
        await callback_query.message.answer("🎁 Bonus feature coming soon!")

    elif data == "withdraw":
        await callback_query.message.answer("💸 Minimum withdrawal is ₹500. Withdrawal panel coming soon!")

    elif data == "set_wallet":
        await callback_query.message.answer("👛 Please reply with your wallet UPI ID to set it.")

    elif data == "support":
        await callback_query.message.answer("🛠 Contact @stockode_support for help.")


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
