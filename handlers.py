from aiogram import types
from aiogram.filters import CommandStart
from aiogram import Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

# FSM for wallet setting
class WalletState(StatesGroup):
    waiting_for_wallet = State()

# ✅ Single, clean handler registration function
def register_handlers(dp: Dispatcher, users: dict, save_users, REF_REWARD: int, MIN_WITHDRAW: int):
    @dp.message(CommandStart())
    async def start_command(message: types.Message):
        uid = str(message.from_user.id)
        if uid not in users:
            ref_by = None
            if message.text.startswith("/start "):
                ref = message.text.split(" ")[1]
                if ref != uid:
                    ref_by = ref
            users[uid] = {"ref_by": ref_by, "wallet": "", "refs": []}
            save_users()

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

    @dp.message(F.text == "Balance")
    async def balance(message: types.Message):
        uid = str(message.from_user.id)
        refs = users.get(uid, {}).get("refs", [])
        bal = len(refs) * REF_REWARD
        await message.answer(f"💰 Your balance is ₹{bal}")

    @dp.message(F.text == "Referrals")
    async def referrals(message: types.Message):
        uid = str(message.from_user.id)
        data = users.get(uid, {})
        total_refs = len(data.get("refs", []))
        link = f"https://t.me/earningtotrade_bot?start={uid}"
        msg = (
            f"➡️ Total invites: {total_refs}\n"
            f"🚥 Per Referral: ₹{REF_REWARD}\n"
            f"🔗 Your invite link:\n{link}"
        )
        await message.answer(msg)

    @dp.message(F.text == "Bonus")
    async def bonus(message: types.Message):
        await message.answer("🎁 No bonus available right now.")

    @dp.message(F.text == "Withdraw")
    async def withdraw(message: types.Message):
        uid = str(message.from_user.id)
        user = users.get(uid, {})
        refs = user.get("refs", [])
        bal = len(refs) * REF_REWARD
        wallet = user.get("wallet", "")

        if not wallet:
            await message.answer("⚠️ You must set your wallet first using 'Set Wallet'.")
            return

        if bal < MIN_WITHDRAW:
            await message.answer(f"❌ Minimum withdrawal is ₹{MIN_WITHDRAW}. You only have ₹{bal}.")
            return

        await message.answer(f"✅ Withdrawal request for ₹{bal} submitted to {wallet}.")

    @dp.message(F.text == "Set Wallet")
    async def set_wallet(message: types.Message, state: FSMContext):
        await message.answer("🔐 Please reply with your UPI ID or Wallet address.")
        await state.set_state(WalletState.waiting_for_wallet)

    @dp.message(WalletState.waiting_for_wallet)
    async def process_wallet(message: types.Message, state: FSMContext):
        uid = str(message.from_user.id)
        users[uid]["wallet"] = message.text.strip()
        save_users()
        await message.answer("✅ Your wallet has been saved successfully!")
        await state.clear()

    @dp.message(F.text == "Support")
    async def support(message: types.Message):
        await message.answer("📞 Contact support: @iamrahulchn")
