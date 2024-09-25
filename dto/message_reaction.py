from dataclasses import dataclass
from datetime import datetime

from dto.types import ChatIdT, MessageIdT, ReactionT, UserIdT


@dataclass(frozen=True)
class MessageReaction:
    chat_id: ChatIdT
    message_id: MessageIdT
    reaction: ReactionT
    reaction_user_id: UserIdT
    message_user_id: UserIdT
    message_date: datetime
