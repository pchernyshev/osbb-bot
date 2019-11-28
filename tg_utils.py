from functools import wraps

from telegram import ChatAction, Update, MessageEntity
from telegram.ext import CommandHandler

TICKET_CMD = "t"


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(
                chat_id=update.effective_message.chat_id, action=action)
            return func(update, context, *args, **kwargs)

        return command_func

    return decorator


def ticket_link(id):
    return f"/{TICKET_CMD}_{id}"


def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        from config import config
        if user_id not in config.LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(update, context, *args, **kwargs)
    return wrapped


class CommandPrefixHandler(CommandHandler):
    def __init__(self, *args, sep='_', suffix_checker=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.sep = sep
        self.suffix_checker = suffix_checker\
            if suffix_checker else self.__dumb_suffix_checker

    @staticmethod
    def __dumb_suffix_checker(*args):
        return True

    def check_update(self, update):
        if isinstance(update, Update) and update.effective_message:
            message = update.effective_message

            if (message.entities
                    and message.entities[0].type == MessageEntity.BOT_COMMAND
                    and message.entities[0].offset == 0):
                command = message.text[1:message.entities[0].length]
                command = command.split('@')
                command.append(message.bot.username)

                command_tokens = command[0].split(self.sep)
                args = command_tokens[1:] + message.text.split()[1:]

                if not (command_tokens[0].lower() in self.command
                        and self.suffix_checker(command_tokens[1:])
                        and command[1].lower() == message.bot.username.lower()):
                    return None

                filter_result = self.filters(update)
                if filter_result:
                    return args, filter_result
                else:
                    return False


send_typing_action = send_action(ChatAction.TYPING)
send_upload_video_action = send_action(ChatAction.UPLOAD_VIDEO)
send_upload_photo_action = send_action(ChatAction.UPLOAD_PHOTO)
