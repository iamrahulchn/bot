import json
import os
from aiogram import types
from aiogram.filters import CommandStart
from aiogram import Dispatcher

# --- Save/Load Wallets from JSON File ---
WALLET_FILE = "wallets.json"

def load_wallets():
    if os.path.exists(WALLET_FILE):
        with open(WALLET_FILE, "r") as f:
            return json.load(f)
    return {}

def save_wallets(wallets):
    with open(WALLET_FILE, "w") as f:
        json.dump(wallets, f)

wallets = load_wallets()


# --- Handler Registration ---
def register_handlers(dp: Dispatcher):

    @dp.message(CommandStart())
    async def start_command(message: types.Message):
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="Balance")],
                [types.KeyboardButton(text="Referrals")],
                [types.KeyboardButton(text="Bonus")],
                [types.KeyboardButton(text="Withdraw")],
                [types.KeyboardButton(text="Set Wallet")],
                [types.KeyboardButton(text="Support")]
            ],
            resize_keyboard=True
        )
        await message.answer("🤖 Welcome to the earning bot!\nPlease select an option:", reply_markup=keyboard)

    @dp.message(lambda message: message.text == "Balance")
    async def balance(message: types.Message):
        uid = str(message.from_user.id)
        ref_count = 0  # Placeholder – you can replace with actual logic
        bal = ref_count * 25
        await message.answer(f"💰 Your balance is ₹{bal}")

    @dp.message(lambda message: message.text == "Referrals")
    async def referrals(message: types.Message):
        uid = str(message.from_user.id)
        link = f"https://t.me/earningtotrade_bot?start={uid}"
        await message.answer(f"👥 You have 0 referrals.\n🚀 Share your link to earn ₹25/referral:\n\n🔗 {link}")

    @dp.message(lambda message: message.text == "Bonus")
    async def bonus(message: types.Message):
        await message.answer("🎁 No bonus available right now.")

    @dp.message(lambda message: message.text == "Withdraw")
    async def withdraw(message: types.Message):
        await message.answer("❌ Minimum withdrawal is ₹500.\nEarn more to withdraw.")

    @dp.message(lambda message: message.text == "Set Wallet")
    async def set_wallet(message: types.Message):
        await message.answer("🔐 Please reply with your UPI ID or Wallet address.\n(Just type it in your next message)")

    @dp.message(lambda message: message.reply_to_message is None and message.text)
    async def save_wallet(message: types.Message):
        uid = str(message.from_user.id)
        text = message.text.strip()

        if "@" in text or "." in text:  # Simple wallet validation (UPI or email-style)
            wallets[uid] = text
            save_wallets(wallets)
            await message.answer(f"✅ Wallet address saved: <code>{text}</code>", parse_mode="HTML")
        else:
            await message.answer("⚠️ That doesn't look like a valid wallet or UPI ID. Please try again.")

    @dp.message(lambda message: message.text == "Support")
    async def support(message: types.Message):
        await message.answer("📞 Contact support: @stockode_support")
