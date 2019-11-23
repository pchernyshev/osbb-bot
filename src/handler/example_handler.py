from telegram import ReplyKeyboardMarkup, KeyboardButton, replymarkup, \
    ReplyKeyboardRemove

import src.gdrive
from echo_example import auth

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
        pass


def test_gdrive(update, context):
    # context.bot.send_message(chat_id=update.effective_chat.id,
    #                          text=src.gdrive.get_all())
    pass

