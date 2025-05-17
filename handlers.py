from aiogram import types
from aiogram.filters import CommandStart
from aiogram import Dispatcher

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
        await message.answer("Welcome to the earning bot!\nPlease select an option:", reply_markup=keyboard)

    @dp.message(lambda message: message.text == "Balance")
    async def balance(message: types.Message):
        await message.answer("💰 Your balance is ₹0")

    @dp.message(lambda message: message.text == "Referrals")
    async def referrals(message: types.Message):
        await message.answer("👥 You have 0 referrals.\nInvite friends using your link to earn ₹25 each.")

    @dp.message(lambda message: message.text == "Bonus")
    async def bonus(message: types.Message):
        await message.answer("🎁 No bonus available right now.")

    @dp.message(lambda message: message.text == "Withdraw")
    async def withdraw(message: types.Message):
        await message.answer("❌ Minimum withdrawal is ₹500.\nEarn more to withdraw.")

    @dp.message(lambda message: message.text == "Set Wallet")
    async def set_wallet(message: types.Message):
        await message.answer("🔐 Please reply with your UPI ID or Wallet address.")

    @dp.message(lambda message: message.text == "Support")
    async def support(message: types.Message):
        await message.answer("📞 Contact support: @stockode_support")
