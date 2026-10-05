from typing import TypedDict


class ChatState(TypedDict):
    message: str
    history: list[dict]
    token: str
    context: str
    response: str