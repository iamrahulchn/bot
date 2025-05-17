from aiogram import types, Router, Bot
from aiogram.filters import CommandStart
from utils import check_subscribed
from db import *

import os

router = Router()
admin_id = int(os.getenv("ADMIN_ID"))

def register_handlers(dp, bot: Bot):
    dp.include_router(router)

@router.message(CommandStart())
async def start(message: types.Message, bot: Bot):
    if not await check_subscribed(message.from_user.id, bot):
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="✅ I've Subscribed", callback_data="check_sub")],
        ])
        return await message.answer("Subscribe to all channels to continue.", reply_markup=keyboard)

    ref_id = int(message.text.split()[1]) if len(message.text.split()) > 1 else None
    add_user(message.from_user.id, ref_id)

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Balance"), types.KeyboardButton(text="Referrals")],
            [types.KeyboardButton(text="Bonus"), types.KeyboardButton(text="Withdraw")],
            [types.KeyboardButton(text="Set Wallet"), types.KeyboardButton(text="Support")],
        ], resize_keyboard=True
    )
    await message.answer("Welcome to Earning to Trade!", reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "check_sub")
async def check_subscription_callback(callback: types.CallbackQuery, bot: Bot):
    if await check_subscribed(callback.from_user.id, bot):
        await callback.message.delete()
        await start(callback.message, bot)
    else:
        await callback.answer("❌ Please join all channels.")

@router.message(lambda msg: msg.text == "Balance")
async def show_balance(message: types.Message):
    bal = get_balance(message.from_user.id)
    await message.answer(f"💰 Your balance: ₹{bal}")

@router.message(lambda msg: msg.text == "Referrals")
async def show_referrals(message: types.Message):
    refs = get_referrals(message.from_user.id)
    await message.answer(f"👥 You have {len(refs)} referrals.")

@router.message(lambda msg: msg.text == "Bonus")
async def show_bonus(message: types.Message):
    bonus = get_bonus(message.from_user.id)
    await message.answer(f"🎁 Referral bonus received: ₹{bonus}")

@router.message(lambda msg: msg.text == "Withdraw")
async def withdraw_request(message: types.Message):
    if request_withdraw(message.from_user.id):
        await message.answer("✅ Withdrawal request submitted.")
    else:
        await message.answer("❌ Minimum ₹500 required to withdraw.")

@router.message(lambda msg: msg.text == "Set Wallet")
async def set_wallet_prompt(message: types.Message):
    await message.answer("Please send your wallet address.")
    @router.message()
    async def receive_wallet_address(msg: types.Message):
        set_wallet(msg.from_user.id, msg.text)
        await msg.answer("✅ Wallet address saved.")

@router.message(lambda msg: msg.text == "Support")
async def support(message: types.Message):
    await message.answer("For support, contact @stockode.official")

# Admin panel
@router.message(lambda msg: msg.from_user.id == admin_id and msg.text == "/admin")
async def admin_panel(message: types.Message):
    report = "\n".join([f"User {uid} - ₹{get_balance(uid)} - Wallet: {get_wallet(uid)}" for uid in withdraw_requests])
    await message.answer(f"🧾 Withdraw Requests:\n{report if report else 'No requests'}")
