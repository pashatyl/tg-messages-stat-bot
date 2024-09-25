from dataclasses import dataclass
from datetime import datetime

from dto.types import ChatIdT, MessageIdT, UserIdT


@dataclass(frozen=True)
class Message:
    chat_id: ChatIdT
    message_id: MessageIdT
    message_user_id: UserIdT
    message_date: datetime
    link: str
    text: str
