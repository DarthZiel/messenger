from datetime import datetime
from typing import AsyncGenerator

from pygments.lexer import default
from sqlalchemy import Column, Integer, DateTime, MetaData, ForeignKey, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import relationship

from src.database import SQLALCHEMY_DATABASE_URL, Base

chat_metadata = MetaData()


class Chat(Base):
    __tablename__ = "Chat"

    id = Column(Integer, primary_key=True, index=True)
    participant_one_id = Column(Integer, ForeignKey('User.id', ondelete='CASCADE'))
    participant_two_id = Column(Integer, ForeignKey('User.id', ondelete='CASCADE'))
    created_at = Column(DateTime, default=datetime.now)
    participant_one = relationship('User', foreign_keys=[participant_one_id], back_populates='participant_one')
    participant_two = relationship('User', foreign_keys=[participant_two_id], back_populates='participant_two')
    messages = relationship('Message', back_populates='chat', cascade='all, delete-orphan')


class Message(Base):
    __tablename__ = "Message"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('User.id', ondelete='CASCADE'))
    chat_id = Column(Integer, ForeignKey('Chat.id', ondelete='CASCADE'))
    text = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    user = relationship("User", back_populates="messages")
    chat = relationship('Chat', back_populates='messages')


engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
