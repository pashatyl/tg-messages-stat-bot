from typing import Optional, Tuple

from databases.base_message_database import BaseMessageDatabase
from dto.message import Message
from dto.types import ChatIdT, MessageIdT


class InMemoryMessageDatabase(BaseMessageDatabase):
    def __init__(self):
        self.messages: dict[Tuple[ChatIdT, MessageIdT], Message] = {}

    def insert(self, message: Message):
        self.messages[(message.chat_id, message.message_id)] = message

    def get(self, chat_id: ChatIdT, message_id: MessageIdT) -> Optional[Message]:
        return self.messages.get((chat_id, message_id), None)
