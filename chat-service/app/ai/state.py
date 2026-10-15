
from typing import TypedDict


class ChatState(TypedDict):
    message: str
    history: list[dict]
    token: str
    user_id: int
    context: str
    response: str
