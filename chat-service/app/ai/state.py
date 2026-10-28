from typing import TypedDict


class ChatState(TypedDict):
    message: str
    history: list[dict]
    user_id: int
    token: str
    mode: str
    document_id: int | None
    context: str
    response: str