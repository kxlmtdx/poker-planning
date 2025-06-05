from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message()
async def echo_message(message: types.Message):
    await message.answer(f"Вы написали: {message.text}")