import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiohttp import web
import json
from handlers import register_handlers
from dotenv import load_dotenv
load_dotenv()

# After creating Dispatcher
register_handlers(dp)



API_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://yourdomain.com/webhook/<token>
PORT = int(os.getenv("PORT", 10000))
CHANNELS = ["@stockodeofficial"]
REF_REWARD = 25
MIN_WITHDRAW = 500
admin_id = 7473008936

DATA_FILE = "users.json"

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

users = load_users()  # user_id: {'ref_by': user_id, 'wallet': str, 'refs': list()}


from aiogram.client.default import DefaultBotProperties

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher(storage=MemoryStorage())

users = {}  # user_id: {'ref_by': user_id, 'wallet': str, 'refs': set()}

# FSM state for wallet input
class WalletState(StatesGroup):
    waiting_for_wallet = State()


# Start command
@dp.message(F.text.startswith("/start"))
async def start(message: Message):
    uid = str(message.from_user.id)
    if uid not in users:
        ref_by = None
        parts = message.text.split(" ")
        if len(parts) > 1:
            ref = parts[1]
            if ref != uid:
                ref_by = ref
        users[uid] = {"ref_by": ref_by, "wallet": "", "refs": []}
        save_users()

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
            member = await bot.get_chat_member(chat_id=channel, user_id=uid)
            if member.status not in ["member", "administrator", "creator"]:
                not_joined.append(channel)
        except Exception:
            not_joined.append(channel)

    if not_joined:
        await callback.answer(
            "❌ You must join all channels to start using the bot. Please join and try again.",
            show_alert=True
        )
    else:
        await callback.answer("✅ Subscription verified! Welcome 🎉", show_alert=True)
        await callback.message.answer(
            "Choose an option below:",
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
    total_refs = len(data.get("refs", []))
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
    await callback.message.answer("🎁 You are not qualified for Bonus!")



# Withdraw (function improved)
@dp.callback_query(F.data == "withdraw")
async def withdraw(callback: types.CallbackQuery):
    uid = str(callback.from_user.id)
    user = users.get(uid, {})
    refs = user.get("refs", [])
    bal = len(refs) * REF_REWARD
    wallet = user.get("wallet", "")

    if not wallet:
        await callback.message.answer("⚠️ You must set your wallet first using 🏦 Set Wallet.")
        return

    if bal < MIN_WITHDRAW:
        await callback.message.answer(f"❌ Minimum withdrawal is ₹{MIN_WITHDRAW}. You only have ₹{bal}.")
        return

    await callback.message.answer(f"✅ Withdrawal request for ₹{bal} submitted to {wallet}.")
    await bot.send_message(admin_id, f"💸 New withdrawal request:\nUser: {uid}\nAmount: ₹{bal}\nWallet: {wallet}")

# 💳 Set Wallet
@dp.callback_query(F.data == "set_wallet")
async def ask_wallet(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(WalletState.waiting_for_wallet)
    await callback.message.answer("💳 Please enter your wallet address (e.g., UPI ID or Paytm/PhonePe/Bank):")

@dp.message(WalletState.waiting_for_wallet)
async def process_wallet(message: types.Message, state: FSMContext):
    uid = str(message.from_user.id)
    users[uid]["wallet"] = message.text.strip()
    save_users()
    await message.answer("✅ Your wallet has been saved successfully!")
    await state.clear()



# --- Webhook handler and server setup ---

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()

async def handle_webhook(request):
    if request.match_info.get('token') == API_TOKEN:
        update = await request.json()
        telegram_update = types.Update.to_object(update)
        await dp.process_update(telegram_update)
        return web.Response(text="OK")
    else:
        return web.Response(status=403, text="Forbidden")

app = web.Application()
app.router.add_post(f'/webhook/{API_TOKEN}', handle_webhook)
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    web.run_app(app, port=PORT)



