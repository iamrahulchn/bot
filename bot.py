import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
from aiohttp import web

API_TOKEN = os.getenv("BOT_TOKEN")
CHANNELS = ["@stockodeofficial"]
REF_REWARD = 25
MIN_WITHDRAW = 500
admin_id = 7473008936

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

USERS_FILE = "users.json"
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

users = load_users()

@dp.message(F.text.startswith("/start"))
async def start(message: Message):
    uid = str(message.from_user.id)
    if uid not in users:
        ref_by = None
        if message.text.startswith("/start "):
            ref = message.text.split(" ")[1]
            if ref != uid:
                ref_by = ref
        users[uid] = {"ref_by": ref_by, "wallet": "", "refs": []}
        save_users(users)

    sub_buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ @stockodeofficial", url="https://t.me/stockodeofficial")],
        [InlineKeyboardButton(text="✔️ Done Subscribed! Click ✅Check", callback_data="check_subs")]
    ])
    await message.answer(
        "<b>🛡️ Subscribe Channels if you want to start the bot and earn from it</b>",
        reply_markup=sub_buttons
    )

@dp.callback_query(F.data == "check_subs")
async def check_subs(callback: types.CallbackQuery):
    uid = str(callback.from_user.id)
    not_joined = []

    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, int(uid))
            if member.status not in ["member", "administrator", "creator"]:
                not_joined.append(channel)
        except:
            not_joined.append(channel)

    if not_joined:
        await callback.message.answer("❌ You must join all channels to start using the bot.\nPlease join and click ✅Check again.")
    else:
        await callback.message.answer("✅ Subscription verified! Welcome 🎉\nChoose an option below:", reply_markup=main_menu())

# Main menu

def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="💰 Balance", callback_data="balance")
    kb.button(text="👥 Referrals", callback_data="referrals")
    kb.button(text="💸 Withdraw", callback_data="withdraw")
    kb.button(text="🏦 Set Wallet", callback_data="set_wallet")
    kb.button(text="🛠 Support", url="https://t.me/iamrahulchn")
    kb.adjust(2)
    return kb.as_markup()

# Referrals
@dp.callback_query(F.data == "referrals")
async def referrals(callback: types.CallbackQuery):
    uid = str(callback.from_user.id)
    data = users.get(uid, {})
    total_refs = len(data.get("refs", []))
    link = f"https://t.me/earningtotrade_bot?start={uid}"
    msg = (
        f"➡️ Total invites: <b>{total_refs}</b>\n"
        f"🚥 Per Referral: ₹{REF_REWARD}\n"
        f"🔗 Your invite link: {link}"
    )
    await callback.message.answer(msg)

# Balance
@dp.callback_query(F.data == "balance")
async def balance(callback: types.CallbackQuery):
    uid = str(callback.from_user.id)
    refs = users.get(uid, {}).get("refs", [])
    bal = len(refs) * REF_REWARD
    await callback.message.answer(f"💰 Your balance is ₹{bal}")

# Set Wallet
@dp.callback_query(F.data == "set_wallet")
async def set_wallet(callback: types.CallbackQuery):
    await callback.message.answer("💳 Please enter your UPI ID to set your wallet.")
    dp.message.register(handle_wallet_input)

async def handle_wallet_input(message: Message):
    uid = str(message.from_user.id)
    wallet = message.text.strip()
    users[uid]["wallet"] = wallet
    save_users(users)
    await message.answer("✅ Wallet set successfully!")

# Withdraw (Placeholder logic)
@dp.callback_query(F.data == "withdraw")
async def withdraw(callback: types.CallbackQuery):
    uid = str(callback.from_user.id)
    refs = users.get(uid, {}).get("refs", [])
    bal = len(refs) * REF_REWARD
    if bal >= MIN_WITHDRAW:
        await callback.message.answer("✅ Your withdrawal request has been submitted.")
    else:
        await callback.message.answer(f"❌ Minimum withdrawal amount is ₹{MIN_WITHDRAW}. Your current balance is ₹{bal}.")

# Webhook setup
async def on_startup(app):
    webhook_url = os.getenv("WEBHOOK_URL")
    await bot.set_webhook(webhook_url)

async def on_shutdown(app):
    await bot.delete_webhook()

async def handle_request(request):
    body = await request.json()
    update = types.Update(**body)
    await dp.feed_update(bot, update)
    return web.Response()

app = web.Application()
app.router.add_post("/webhook", handle_request)
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    web.run_app(app, port=int(os.getenv("PORT", 10000)))
