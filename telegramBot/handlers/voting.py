from aiogram import Router, types, Bot, F
from aiogram.types import CallbackQuery
import uuid

from models.database import Database

router = Router()

@router.callback_query(F.data.startswith("vote:"))
async def process_vote(callback: CallbackQuery, db: Database, bot: Bot):
    _, issue_id_str, value = callback.data.split(":")
    try:
        issue_id = uuid.UUID(issue_id_str)
        value = float(value)
    except (ValueError, AttributeError):
        await callback.answer("Некорректные данные голосования")
        return
    
    user_id = callback.from_user.id
    
    db.cursor.execute(
        "SELECT 1 FROM Issues WHERE IssueId = ? AND Status = 'Voting'",
        (issue_id,)
    )
    if not db.cursor.fetchone():
        await callback.answer("Голосование по этой задаче завершено")
        return
    
    success = db.submit_vote(issue_id, user_id, value)
    if not success:
        await callback.answer("Ошибка при сохранении голоса")
        return
    
    await callback.answer(f"Ваш голос: {value} принят!")
    
    votes = db.get_current_votes(issue_id)
    median = db.get_median_estimate(issue_id)
    
    message_text = f"Текущие результаты голосования:\n\n"
    for vote in votes:
        message_text += f"{vote['Username']}: {vote['Estimate']}\n"
    message_text += f"\nМедианная оценка: {median if median else 'еще не рассчитана'}"

    db.cursor.execute(
        "SELECT GroupId FROM Sessions WHERE SessionId = "
        "(SELECT SessionId FROM Issues WHERE IssueId = ?)",
        (issue_id,)
    )
    group_id = db.cursor.fetchone()[0]

    db.cursor.execute(
        "SELECT MessageId FROM VotingMessages WHERE IssueId = ?",
        (issue_id,)
    )
    existing_message = db.cursor.fetchone()
    
    try:
        if existing_message:
            await bot.edit_message_text(
                chat_id=group_id,
                message_id=existing_message[0],
                text=message_text
            )
        else:
            sent_message = await bot.send_message(
                chat_id=group_id,
                text=message_text
            )
            db.cursor.execute(
                "INSERT INTO VotingMessages (IssueId, MessageId) VALUES (?, ?)",
                (issue_id, sent_message.message_id)
            )
            db.conn.commit()
    except Exception as e:
        print(f"Ошибка при обновлении результатов: {e}")