from datetime import datetime
from http.client import HTTPException

from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.chat.models import Message
from src.history.schemas import MessageResponse


class HistoryRepository:

    @staticmethod
    async def write_message(db: AsyncSession, user_id: int, chat_id: int, message_text: str) -> Message:
        # Создание нового сообщения
        new_message = Message(user_id=user_id, chat_id=chat_id, text=message_text)

        db.add(new_message)
        await db.commit()  # Сохраняем изменения в базе данных
        await db.refresh(
            new_message)  # Обновляем объект, чтобы получить значения, присвоенные базой данных (например, id)

        return new_message

    @staticmethod
    async def get_messages_by_date(
        db: AsyncSession,
        chat_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[MessageResponse]:
        # Создаем запрос с join
        stmt = (
            select(Message, User.email)  # Запрашиваем поля Message и email пользователя
            .join(User, User.id == Message.user_id)  # Убедитесь, что join происходит по правильному полю
            .where(
                Message.chat_id == chat_id,
                Message.created_at >= start_date,
                Message.created_at <= end_date
            )
        )

        result = await db.execute(stmt)
        messages = result.all()  # Получаем все результаты

        if not messages:
            raise HTTPException(status_code=404, detail="Сообщений не найдено за указанный период.")

        # Преобразуем результаты в MessageResponse
        messages_response = [
            MessageResponse(
                id=message[0].id,
                user_id=message[0].user_id,
                chat_id=message[0].chat_id,
                text=message[0].text,
                created_at=message[0].created_at,
                email=message[1]
            )
            for message in messages
        ]

        return messages_response