from abc import ABC, abstractmethod
from typing import Optional

from dto.message import Message
from dto.types import ChatIdT, MessageIdT


class BaseMessageDatabase(ABC):
    @abstractmethod
    def insert(self, message: Message): ...

    @abstractmethod
    def get(self, chat_id: ChatIdT, message_id: MessageIdT) -> Optional[Message]: ...
