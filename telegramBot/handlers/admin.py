from aiogram import Router, types, Bot, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import uuid
import json

from models.database import Database

router = Router()

class SessionStates(StatesGroup):
    waiting_for_session_name = State()
    waiting_for_members = State()

class IssueStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    confirming_issue = State()

@router.message(Command("start_session"))
async def cmd_start_session(message: types.Message, state: FSMContext, db: Database):
    if not message.chat.type == "supergroup":
        await message.answer("Сессии можно создавать только в групповых чатах.")
        return
    
    db.cursor.execute(
        "SELECT 1 FROM Users WHERE UserId = ? AND IsScrumMaster = 1",
        (message.from_user.id,)
    )
    if not db.cursor.fetchone():
        await message.answer("Только Scrum-мастер может создавать сессии.")
        return
    
    await message.answer("Введите название сессии планирования:")
    await state.set_state(SessionStates.waiting_for_session_name)