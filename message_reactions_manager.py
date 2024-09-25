from datetime import datetime

from databases.base_message_database import BaseMessageDatabase
from databases.base_message_reaction_database import BaseMessageReactionDatabase
from dto.message import Message
from dto.message_reaction import MessageReaction
from dto.types import ChatIdT, MessageIdT, ReactionT, UserIdT


class MessageReactionsManager:
    def __init__(
        self,
        message_database: BaseMessageDatabase,
        message_reaction_database: BaseMessageReactionDatabase,
    ):
        self._message_reaction_database = message_reaction_database
        self._message_database = message_database

    def add_message(
        self,
        chat_id: ChatIdT,
        message_id: MessageIdT,
        message_user_id: UserIdT,
        message_date: datetime,
        link: str,
        text: str,
    ) -> None:
        self._message_database.insert(
            Message(
                chat_id=chat_id,
                message_id=message_id,
                message_user_id=message_user_id,
                message_date=message_date,
                link=link,
                text=text,
            )
        )

    def add_reaction(
        self,
        chat_id: ChatIdT,
        message_id: MessageIdT,
        reaction: ReactionT,
        reaction_user_id: UserIdT,
    ):
        message = self._message_database.get(chat_id, message_id)
        if message is None:
            return
        self._message_reaction_database.insert(
            MessageReaction(
                chat_id=chat_id,
                message_id=message_id,
                reaction=reaction,
                reaction_user_id=reaction_user_id,
                message_user_id=message.message_user_id,
                message_date=message.message_date,
            )
        )

    def remove_reaction(
        self,
        chat_id: ChatIdT,
        message_id: MessageIdT,
        reaction: ReactionT,
        reaction_user_id: UserIdT,
    ):
        message = self._message_database.get(chat_id, message_id)
        if message is None:
            return
        self._message_reaction_database.delete(
            MessageReaction(
                chat_id=chat_id,
                message_id=message_id,
                reaction=reaction,
                reaction_user_id=reaction_user_id,
                message_user_id=message.message_user_id,
                message_date=message.message_date,
            )
        )
