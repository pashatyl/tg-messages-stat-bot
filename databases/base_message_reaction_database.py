from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterator

from dto.message_reaction import MessageReaction
from dto.types import ChatIdT, MessageIdT, ReactionT, UserIdT


@dataclass(frozen=True)
class BestMessage:
    message_id: MessageIdT
    reaction_counts: Dict[ReactionT, int]


@dataclass(frozen=True)
class BestUser:
    user: UserIdT
    reaction_counts: Dict[ReactionT, int]


class BaseMessageReactionDatabase(ABC):
    @abstractmethod
    def insert(self, reaction: MessageReaction) -> None: ...

    @abstractmethod
    def delete(self, reaction: MessageReaction) -> None: ...

    @abstractmethod
    def get_top_messages(
        self, chat_id: ChatIdT, start: datetime, end: datetime, limit: int
    ) -> Iterator[BestMessage]: ...

    @abstractmethod
    def get_top_users(
        self, chat_id: ChatIdT, start: datetime, end: datetime, limit: int
    ) -> Iterator[BestUser]: ...
