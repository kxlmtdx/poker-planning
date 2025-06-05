from aiogram import Router, types
from aiogram.filters import Command

from keyboards.main_menu import main_menu_kb

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Халло",
        reply_markup=main_menu_kb()
    )