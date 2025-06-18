from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import uuid

from models.database import Database

router = Router()

class SessionStates(StatesGroup):
    waiting_for_session_name = State()
    waiting_for_members = State()

@router.message(Command("start_session"))
async def cmd_start_session(message: types.Message, state: FSMContext, db: Database):
    db.cursor.execute(
        "SELECT 1 FROM Users WHERE UserId = ? AND IsScrumMaster = 1",
        (message.from_user.id,)
    )
    if not db.cursor.fetchone():
        await message.answer("Только Scrum-мастер может создавать сессии.")
        return
    
    await message.answer("Введите название сессии планирования:")
    await state.set_state(SessionStates.waiting_for_session_name)

@router.message(SessionStates.waiting_for_session_name)
async def process_session_name(message: types.Message, state: FSMContext, db: Database):
    session_name = message.text
    group_id = message.chat.id
    
    db.cursor.execute(
        "INSERT INTO Groups (GroupId, GroupName, CreatedBy) VALUES (?, ?, ?)",
        (group_id, session_name, message.from_user.id)
    )
    
    session_id = uuid.uuid4()
    db.cursor.execute(
        "INSERT INTO Sessions (SessionId, GroupId, CreatedBy) VALUES (?, ?, ?)",
        (session_id, group_id, message.from_user.id)
    )
    
    db.cursor.execute(
        "INSERT INTO GroupMembers (GroupId, UserId) VALUES (?, ?)",
        (group_id, message.from_user.id)
    )
    
    db.conn.commit()
    
    await state.update_data(session_id=session_id, group_id=group_id)
    await message.answer(
        f"Сессия '{session_name}' создана. Теперь добавьте участников командой /add_member @username",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Завершить добавление", callback_data="finish_adding_members")]
        ])
    )
    await state.set_state(SessionStates.waiting_for_members)

@router.message(Command("add_member"))
async def cmd_add_member(message: types.Message, state: FSMContext, db: Database, bot: Bot):
    current_state = await state.get_state()
    if current_state != SessionStates.waiting_for_members:
        await message.answer("Сначала создайте сессию командой /start_session")
        return
    
    if not message.reply_to_message or not message.reply_to_message.entities:
        await message.answer("Укажите username участника в формате /add_member @username")
        return
    
    username = message.text.split()[1].replace("@", "")
    
    try:
        chat_member = await bot.get_chat_member(message.chat.id, username)
        user_id = chat_member.user.id
        
        db.get_or_create_user(
            user_id=user_id,
            username=username,
            first_name=chat_member.user.first_name,
            last_name=chat_member.user.last_name
        )
        
        data = await state.get_data()
        db.cursor.execute(
            "INSERT INTO GroupMembers (GroupId, UserId) VALUES (?, ?)",
            (data['group_id'], user_id)
        )
        db.conn.commit()
        
        await message.answer(f"Участник @{username} добавлен в сессию")
    except Exception as e:
        await message.answer(f"Ошибка добавления участника: {e}")

@router.callback_query(F.data == "finish_adding_members", SessionStates.waiting_for_members)
async def finish_adding_members(callback: types.CallbackQuery, state: FSMContext, db: Database):
    data = await state.get_data()
    session_id = data['session_id']
    
    db.cursor.execute(
        "UPDATE Sessions SET Status = 'Active' WHERE SessionId = ?",
        (session_id,)
    )
    db.conn.commit()
    
    await callback.message.edit_text(
        "Сессия планирования начата! Теперь вы можете создавать задачи командой /new_issue"
    )
    await state.clear()