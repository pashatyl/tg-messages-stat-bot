import logging
from datetime import timedelta

from telegram import ReactionType, Update
from telegram.constants import UpdateType
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    MessageReactionHandler,
    filters,
)

from databases.in_memory_message_database import InMemoryMessageDatabase
from databases.in_memory_message_reaction_database import InMemoryMessageReactionDatabase
from dto.types import (
    ChatIdT,
    MessageIdT,
    ReactionT,
    UserIdT,
)
from message_reactions_manager import MessageReactionsManager

LOGGER = logging.getLogger(__name__)
reactions_database = InMemoryMessageReactionDatabase()
messages_database = InMemoryMessageDatabase()
reactions_manager = MessageReactionsManager(
    messages_database,
    reactions_database,
)
LAST_N_DAYS = 7

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Unknown hit")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command.",
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Start hit")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I'm a bot, please talk to me!",
    )


async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Stat hit")
    # TODO: Add parameter for days
    start_date = update.message.date - timedelta(days=LAST_N_DAYS)
    end_date = update.message.date
    chat_id = ChatIdT(update.effective_chat.id)
    top_messages = list(reactions_database.get_top_messages(
        chat_id,
        start_date,
        end_date,
        5,
    ))
    top_messages_strings = []
    for message_reactions in top_messages:
        message = messages_database.get(chat_id, message_reactions.message_id)
        top_messages_strings.append(f"[{message.text}]({message.link}): {message_reactions.reaction_counts}")

    top_users = list(reactions_database.get_top_users(
        chat_id,
        start_date,
        end_date,
        5,
    ))

    top_users_strings = []
    for user_reactions in top_users:
        top_users_strings.append(f"@{user_reactions.user}: {user_reactions.reaction_counts}")

    top_message_string = '\n'.join(top_messages_strings)
    top_users_string = '\n'.join(top_users_strings)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Top messages from last {LAST_N_DAYS} days:\n{top_message_string}\n"
             f"Best publishers from last {LAST_N_DAYS} days:\n{top_users_string}\n\n"
             f"#MessagesStat",
        parse_mode="Markdown",
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Message received")
    if update.message is None or update.message.from_user is None:
        return
    reactions_manager.add_message(
        ChatIdT(update.message.chat.id),
        MessageIdT(update.message.message_id),
        UserIdT(update.message.from_user.username),
        update.message.date,
        f"https://t.me/c/{str(update.message.chat.id)[4:]}/{update.message.message_id}",
        update.message.text or "EMPTY",
    )


async def reaction(update: Update, context: CallbackContext):
    print("Reaction received")
    # TODO: replace add and remove with update logic as new is an actual state to the event time
    message_reaction = update.message_reaction
    print(message_reaction.old_reaction)
    print(message_reaction.new_reaction)
    if (
        message_reaction.old_reaction
        and message_reaction.old_reaction[0].type == ReactionType.EMOJI
    ):
        reactions_manager.remove_reaction(
            ChatIdT(message_reaction.chat.id),
            MessageIdT(message_reaction.message_id),
            ReactionT(message_reaction.old_reaction[0].emoji),
            UserIdT(message_reaction.user.username),
        )
    if (
        message_reaction.new_reaction
        and message_reaction.new_reaction[0].type == ReactionType.EMOJI
    ):
        reactions_manager.add_reaction(
            ChatIdT(message_reaction.chat.id),
            MessageIdT(message_reaction.message_id),
            ReactionT(message_reaction.new_reaction[0].emoji),
            UserIdT(message_reaction.user.username),
        )


class App:
    def __init__(self, token: str):
        self._application = ApplicationBuilder().token(token).build()
        self._application.add_handler(CommandHandler("start", start))
        self._application.add_handler(CommandHandler("stat", stat))
        self._application.add_handler(MessageReactionHandler(reaction))
        self._application.add_handler(MessageHandler(filters.ALL, message_handler))
        # Must be last as a fallback
        self._application.add_handler(MessageHandler(filters.COMMAND, unknown))

    def start(self):
        LOGGER.info("Run polling")
        print("Run")
        self._application.run_polling(
            allowed_updates=[
                UpdateType.MESSAGE_REACTION,
                UpdateType.MESSAGE_REACTION_COUNT,
                UpdateType.MESSAGE,
            ]
        )
