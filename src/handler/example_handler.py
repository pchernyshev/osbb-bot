import json

from src import REGISTERED_BRIDGES
from src.gdrive import test_get_request




def test_gdrive(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=test_get_request())


def try_authorize(update, context):
    # TODO: Attach contact info
    is_authorized = db.is_authorized_contact()
    response = 'Welcome' if is_authorized else "You're not welcomed here"

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=response)


def dummy_greeter(update, context):
    pass