import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

API_TOKEN = os.getenv("BOT_TOKEN")
CHANNELS = ["@stockodeofficial"]
REF_REWARD = 25
MIN_WITHDRAW = 500
admin_id = 7473008936

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

users = {}  # user_id: {'ref_by': user_id, 'wallet': str, 'refs': set()}

# FSM state for wallet input
class WalletState(StatesGroup):
    waiting_for_wallet = State()


# Start command
@dp.message(F.text.startswith("/start"))
async def start(message: Message):
    uid = message.from_user.id
    if uid not in users:
        ref_by = None
        if message.text.startswith("/start "):
            ref = message.text.split(" ")[1]
            if ref != str(uid):
                ref_by = int(ref)
        users[uid] = {"ref_by": ref_by, "wallet": "", "refs": set()}
        if ref_by and ref_by in users:
            users[ref_by]["refs"].add(uid)

    welcome = (
        "🤖 <b>Welcome to Referwala By Stockode Referral Bot</b>\n\n"
        "✔️ Refer and Earn Cash\n\n"
        "🛡️ <b>Subscribe to all platforms to activate your referral bot:</b>\n\n"
        "✅ Telegram Channels (Required)\n📸 Instagram & ▶️ YouTube (Optional but appreciated!)"

    )
    sub_buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ @stockodeofficial", url="https://t.me/stockodeofficial")],
        [InlineKeyboardButton(text="📸 Follow on Instagram", url="https://instagram.com/stockode.official")],
        [InlineKeyboardButton(text="▶️ Subscribe on YouTube", url="https://youtube.com/@stockodeofficial")],
        [InlineKeyboardButton(text="✔️ Done Subscribed! Click ✅Check", callback_data="check_subs")]
    
    ])
    await message.answer(welcome, reply_markup=sub_buttons)


# Check subscription
@dp.callback_query(F.data == "check_subs")
async def check_subs(callback: types.CallbackQuery):
    uid = callback.from_user.id
    not_joined = []

    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, uid)
            if member.status not in ["member", "administrator", "creator"]:
                not_joined.append(channel)
        except:
            not_joined.append(channel)

    if not_joined:
        await callback.message.answer(
            "❌ You must join all channels to start using the bot.\nPlease join and click ✅Check again."
        )
    else:
        await callback.message.answer(
            "✅ Subscription verified! Welcome 🎉\nChoose an option below:",
            reply_markup=main_menu()
        )


# Main menu
def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="💰 Balance", callback_data="balance")
    kb.button(text="👥 Referrals", callback_data="referrals")
    kb.button(text="🎁 Bonus", callback_data="bonus")
    kb.button(text="💸 Withdraw", callback_data="withdraw")
    kb.button(text="🏦 Set Wallet", callback_data="set_wallet")
    kb.button(text="🛠 Support", url="https://instagram.com/stockode.official")
    kb.adjust(2)
    return kb.as_markup()


# Referrals
@dp.callback_query(F.data == "referrals")
async def referrals(callback: types.CallbackQuery):
    uid = callback.from_user.id
    data = users.get(uid, {})
    total_refs = len(data.get("refs", set()))
    link = f"https://t.me/earningtotrade_bot?start={uid}"
    msg = (
        f"➡️ <b>Total invites:</b> {total_refs}\n"
        f"🚥 <b>Per Referral:</b> ₹{REF_REWARD}\n"
        f"🔗 <b>Your invite link:</b> {link}"
    )
    await callback.message.answer(msg)


# Balance
@dp.callback_query(F.data == "balance")
async def balance(callback: types.CallbackQuery):
    uid = callback.from_user.id
    refs = users.get(uid, {}).get("refs", set())
    bal = len(refs) * REF_REWARD
    await callback.message.answer(f"💰 <b>Your balance is ₹{bal}</b>")


# Bonus (not yet implemented)
@dp.callback_query(F.data == "bonus")
async def bonus(callback: types.CallbackQuery):
    await callback.message.answer("🎁 Bonus system coming soon!")


# Withdraw (not yet implemented)
@dp.callback_query(F.data == "withdraw")
async def withdraw(callback: types.CallbackQuery):
    await callback.message.answer("💸 Withdrawal system coming soon!")


# 💳 Set Wallet
@dp.callback_query(F.data == "set_wallet")
async def ask_wallet(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(WalletState.waiting_for_wallet)
    await callback.message.answer("💳 Please enter your wallet address (e.g., UPI ID or Paytm/PhonePe/Bank):")

@dp.message(WalletState.waiting_for_wallet)
async def save_wallet(message: types.Message, state: FSMContext):
    uid = message.from_user.id
    wallet = message.text.strip()

    if uid in users:
        users[uid]["wallet"] = wallet
    else:
        users[uid] = {"ref_by": None, "wallet": wallet, "refs": set()}

    await message.answer(f"✅ Wallet address saved: <code>{wallet}</code>")
    await state.clear()


# Background polling
async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8000))
    asyncio.run(main())
