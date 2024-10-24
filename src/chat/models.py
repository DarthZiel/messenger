from datetime import datetime
from typing import AsyncGenerator
from sqlalchemy import Column, Integer, DateTime, MetaData, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


from src.database import SQLALCHEMY_DATABASE_URL, Base

chat_metadata = MetaData()


class Chat(Base):
    __tablename__ = "Chat"

    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey('User.id', ondelete='CASCADE'))
    user2_id = Column(Integer, ForeignKey('User.id', ondelete='CASCADE'))
    created_at = Column(DateTime, default=datetime.now)


class Message(Base):
    __tablename__ = "Message"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey('Chat.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('User.id', ondelete='CASCADE'))
    created_at = Column(DateTime, default=datetime.now)


engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


