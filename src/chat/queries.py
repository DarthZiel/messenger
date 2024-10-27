from sqlalchemy.ext.asyncio import AsyncSession
from src.chat.models import Message

async def create_message(db: AsyncSession, user_id: int, message_text: str) -> Message:
    new_message = Message(user_id=user_id, text=message_text)
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message