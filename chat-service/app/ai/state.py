from typing import TypedDict


class ChatState(TypedDict):
    message: str
    history: list[dict]
    response: str