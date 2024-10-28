from pydantic import BaseModel



class GetChatByEmail:
    email: str

class Participants(BaseModel):
    participant_one: int
    participant_two: int
