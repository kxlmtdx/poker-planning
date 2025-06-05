from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_kb():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Кнопка 1")],
            [KeyboardButton(text="Кнопка 2")],
        ],
        resize_keyboard=True
    )
    return keyboard