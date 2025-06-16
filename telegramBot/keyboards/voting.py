from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_voting_options_kb(issue_id: int):
    options = [0, 0.5, 1, 2, 3, 5, 8, 13, 20, 40, 100]
    
    buttons = []
    row = []
    for i, option in enumerate(options):
        row.append(InlineKeyboardButton(
            text=str(option),
            callback_data=f"vote:{issue_id}:{option}"
        ))
        if (i + 1) % 3 == 0 or i == len(options) - 1:
            buttons.append(row)
            row = []
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)