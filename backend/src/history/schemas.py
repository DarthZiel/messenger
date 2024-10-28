from pydantic import BaseModel
from datetime import datetime



class MessageResponse(BaseModel):
    id: int
    user_id: int
    chat_id: int
    text: str
    created_at: datetime
    email: str
    class Config:
        orm_mode = True
