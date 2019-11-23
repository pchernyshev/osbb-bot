import json


from telegram import ReplyKeyboardMarkup, KeyboardButton, replymarkup, \
    ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

import src.gdrive
from echo_example import auth

from src import REGISTERED_BRIDGES

db = None
config = json.loads(open('config/db.json').read())
bridge_type = config.pop('type')


for bridge in REGISTERED_BRIDGES:
    if bridge.responds_to(bridge_type):
        db = bridge(config)
        break
else:
    raise LookupError(f"No bridge found for {bridge_type}")


GREETING_FIRST_TIME = "Hey, I'm a bot. You are not authorized, give me your " \
                      "phone number, boots and motorcycle"
GREETING_AUTH = "Hey, <username>"


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!",
        reply_markup=ReplyKeyboardMarkup.from_row(
            [KeyboardButton(text="Share phone number", request_contact=True)],
            one_time_keyboard=True))


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=update.message.text)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Sorry, I didn't understand that command.")


def got_contact(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Checking for authorization",
                             reply_markup=ReplyKeyboardRemove())
    # TODO: actual check
    apt = auth.authenticate("+380501234567")
    if apt != auth.NO_PHONE_FOUND:
        #TODO: registration sequence
        pass
    else:
        #TODO: main men
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Welcome to main menu!",
                                 reply_markup=InlineKeyboardMarkup.from_row(
                                     [InlineKeyboardButton(text="Show FAQ", callback_data="FAQ"),
                                      InlineKeyboardButton(text="My opened requests", callback_data="MyRequests"),
                                      InlineKeyboardButton(text="Create new request", callback_data="NewRequest")],
                                     one_time_keyboard=True))
        pass


def test_gdrive(update, context):
    # context.bot.send_message(chat_id=update.effective_chat.id,
    #                          text=src.gdrive.get_all())
    pass


def try_authorize(update, context):
    # TODO: Attach contact info
    is_authorized = db.is_authorized_contact()
    response = 'Welcome' if is_authorized else "You're not welcomed here"

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=response)
