from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter
from src.database import get_db
from src.history.repository import HistoryRepository
from src.history.schemas import MessageResponse
from typing import List

router = APIRouter(
    prefix='/history',
    tags=['history']
)


@router.get("/{chat_id}", response_model=List[MessageResponse])  # Возвращаем список моделей сообщений
async def get_messages_by_date(
        chat_id: int,
        start_date: datetime,
        end_date: datetime,
        session: AsyncSession = Depends(get_db)  # Используем AsyncSession для асинхронных операций
):
    start_date = datetime.combine(start_date, datetime.min.time())
    end_date = datetime.combine(end_date, datetime.max.time())

    # Используем метод репозитория для получения сообщений
    messages = await HistoryRepository.get_messages_by_date(session, chat_id, start_date, end_date)
    return messages  # Возвращаем список сообщений