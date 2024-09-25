import heapq
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterator, Tuple, DefaultDict

from databases.base_message_reaction_database import (
    BaseMessageReactionDatabase,
    BestMessage,
    BestUser,
)
from dto.message_reaction import MessageReaction
from dto.types import ChatIdT, MessageIdT, ReactionT, UserIdT


@dataclass
class StorageValue:
    message_user_id: UserIdT
    reactions_user_id: UserIdT
    reactions: Dict[ReactionT, int]
    reactions_count: int
    message_date: datetime


class InMemoryMessageReactionDatabase(BaseMessageReactionDatabase):
    def __init__(self):
        self._storage: Dict[Tuple[ChatIdT, MessageIdT], StorageValue] = {}

    def insert(self, message_reaction: MessageReaction) -> None:
        key = (message_reaction.chat_id, message_reaction.message_id)
        if key not in self._storage:
            self._storage[key] = StorageValue(
                message_reaction.message_user_id,
                message_reaction.reaction_user_id,
                defaultdict(lambda: 0),
                0,
                message_reaction.message_date,
            )
        self._storage[key].reactions[message_reaction.reaction] += 1
        self._storage[key].reactions_count += 1

    def delete(self, message_reaction: MessageReaction) -> None:
        key = (message_reaction.chat_id, message_reaction.message_id)
        if (
            key in self._storage
            and message_reaction.reaction in self._storage[key].reactions
        ):
            self._storage[key].reactions[message_reaction.reaction] -= 1
            self._storage[key].reactions_count -= 1

    def get_top_messages(
        self,
        chat_id: ChatIdT,
        start: datetime,
        end: datetime,
        limit: int,
    ) -> Iterator[BestMessage]:
        """Returns ``limit`` items with most reactions"""
        top = heapq.nlargest(
            limit,
            self._storage.items(),
            key=lambda x: x[1].reactions_count,
        )
        for (chat_id, message_id), value in top:
            yield BestMessage(message_id, dict(value.reactions))

    def get_top_users(
        self,
        chat_id: ChatIdT,
        start: datetime,
        end: datetime,
        limit: int,
    ) -> Iterator[BestUser]:
        """Returns ``limit`` users with most reactions in current chat"""
        # TODO: support time filtering

        @dataclass
        class UserMessageReactions:
            count: int
            reactions: DefaultDict[ReactionT, int]

        users_counts: Dict[UserIdT, UserMessageReactions] = defaultdict(
            lambda: UserMessageReactions(0, defaultdict(lambda: 0))
        )
        for _, value in self._storage.items():
            users_counts[value.message_user_id].count += value.reactions_count
            for reaction, count in value.reactions.items():
                users_counts[value.message_user_id].reactions[reaction] += count
        top = heapq.nlargest(
            limit,
            users_counts.items(),
            key=lambda x: x[1].count,
        )
        for user_id, user_message_reaction in top:
            yield BestUser(user_id, dict(user_message_reaction.reactions))
