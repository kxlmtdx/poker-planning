from aiogram import Router, types, Bot, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import uuid
import json

from models.database import Database
from keyboards.voting import get_voting_options_kb

router = Router()

class SessionStates(StatesGroup):
    waiting_for_session_name = State()
    waiting_for_members = State()

class IssueStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    confirming_issue = State()

#session op
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

@router.message(Command("close_session"))
async def cmd_close_session(message: types.Message, db: Database, bot: Bot):
    master_id = message.from_user.id

    db.cursor.execute(
        "SELECT SessionId FROM Sessions WHERE CreatedBy = ? AND Status = 'Active'",
        (master_id,)
    )
    session = db.cursor.fetchone()
    
    if not session:
        await message.answer("Нет активной сессии.")
        return
    
    session_id = session[0]

    db.cursor.execute(
        "UPDATE Issues SET Status = 'Completed', FinalEstimate = dbo.CalculateMedianEstimate(IssueId) "
        "WHERE SessionId = ? AND Status = 'Voting'",
        (session_id,)
    )

    db.close_session(session_id)

    db.cursor.execute(
        "SELECT i.Title, i.FinalEstimate, v.Estimate, u.Username "
        "FROM Issues i "
        "LEFT JOIN Votes v ON i.IssueId = v.IssueId AND v.IsCurrent = 1 "
        "LEFT JOIN Users u ON v.UserId = u.UserId "
        "WHERE i.SessionId = ?",
        (session_id,)
    )
    
    results = {}
    for row in db.cursor.fetchall():
        title, final_estimate, estimate, username = row
        if title not in results:
            results[title] = {
                "final_estimate": float(final_estimate) if final_estimate else None,
                "votes": []
            }
        if estimate and username:
            results[title]["votes"].append({
                "username": username,
                "estimate": float(estimate)
            })

    results_json = json.dumps(results, ensure_ascii=False, indent=2)
    db.cursor.execute(
        "INSERT INTO Results (ResultId, SessionId, ResultData, GeneratedDate, SentToMaster) "
        "VALUES (NEWID(), ?, ?, GETDATE(), 1)",
        (session_id, results_json)
    )
    db.conn.commit()

    await bot.send_message(
        master_id,
        f"Результаты голосования:\n<code>{results_json}</code>",
        parse_mode="HTML"
    )

    await bot.send_message(
        message.chat.id,
        "Сессия планирования завершена. Результаты отправлены Scrum-мастеру."
    )

#issue op
@router.message(Command("new_issue"))
async def cmd_new_issue(message: types.Message, state: FSMContext, db: Database):
    db.cursor.execute(
        "SELECT TOP 1 SessionId FROM Sessions WHERE CreatedBy = ? AND Status = 'Active'",
        (message.from_user.id,)
    )
    session = db.cursor.fetchone()
    
    if not session:
        await message.answer("Нет активной сессии. Сначала создайте сессию командой /start_session")
        return
    
    await state.update_data(session_id=session[0], group_id=message.chat.id)
    await message.answer("Введите название задачи:")
    await state.set_state(IssueStates.waiting_for_title)

@router.message(IssueStates.waiting_for_title)
async def process_issue_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание задачи (или нажмите /skip для пропуска):")
    await state.set_state(IssueStates.waiting_for_description)

@router.message(Command("skip"), IssueStates.waiting_for_description)
async def skip_description(message: types.Message, state: FSMContext):
    await process_issue_confirmation(message, state)

@router.message(IssueStates.waiting_for_description)
async def process_issue_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await process_issue_confirmation(message, state)

async def process_issue_confirmation(message: types.Message, state: FSMContext):
    data = await state.get_data()
    title = data['title']
    description = data.get('description', 'Нет описания')
    
    confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить", callback_data="confirm_issue")],
        [InlineKeyboardButton(text="Отменить", callback_data="cancel_issue")]
    ])
    
    await message.answer(
        f"Вы создаете задачу:\n\n"
        f"Название: {title}\n"
        f"Описание: {description}\n\n"
        f"Начать голосование?",
        reply_markup=confirm_kb
    )
    await state.set_state(IssueStates.confirming_issue)

@router.callback_query(F.data == "confirm_issue", IssueStates.confirming_issue)
async def confirm_issue(callback: types.CallbackQuery, state: FSMContext, db: Database, bot: Bot):
    data = await state.get_data()
    title = data['title']
    description = data.get('description')
    session_id = data['session_id']
    master_id = callback.from_user.id

    issue_id = db.create_issue(
        session_id=session_id,
        title=title,
        description=description,
        created_by=master_id
    )
    
    await callback.message.edit_text(f"Голосование за задачу '{title}' начато!")
    await state.clear()

    participants = db.get_session_participants(session_id)
    for participant in participants:
        try:
            await bot.send_message(
                participant['UserId'],
                f"Новая задача для оценки:\n\n"
                f"Название: {title}\n"
                f"Описание: {description or 'Нет описания'}",
                reply_markup=get_voting_options_kb(issue_id)
            )
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {participant['UserId']}: {e}")

    await bot.send_message(
        chat_id=data['group_id'],
        text=f"Начато голосование за задачу: {title}\n"
             f"Участники: {len(participants)} человек"
    )