import re

from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, \
    Filters, CallbackQueryHandler

from Authenticator import Authenticator, SAMPLE_DB
from config.config import VALID_BUILDINGS, MAX_VALID_APPARTMENT
from src.handler.const import AuthStates, Flows
from src.handler.local_storage import LOCAL_STORAGE
from src.handler.main_loop_conversation import show_main_menu

GREETING_FIRST_TIME = "Hey, I'm a bot. You are not authorized, give me your " \
                      "phone number, boots and motorcycle"
GREETING_AUTH = "Hey, <username>"

CHECK_AUTH_VALUE = "Check"


auth = Authenticator(SAMPLE_DB)

def greeter(update, context):
    chat_id = update.effective_chat.id
    client = LOCAL_STORAGE[chat_id]
    client.update_locale(update.effective_user.language_code)

    if client.auth_state == AuthStates.AUTHORIZED_STATE:
        context.bot.send_message(chat_id=chat_id, text=GREETING_AUTH)
        show_main_menu(update, context)
        return -1
    else:
        context.bot.send_message(
            chat_id=chat_id, text=GREETING_FIRST_TIME,
            reply_markup=ReplyKeyboardMarkup.from_row(
                [KeyboardButton(text="Share phone number",
                                request_contact=True)],
                one_time_keyboard=True))
        return AuthStates.PHONE_CHEKING_STATE


def got_contact(update, context):
    chat_id = update.effective_chat.id
    if not re.match(r'\+[1-9][0-9]{10,}', update.message.contact.phone_number):
        context.bot.send_message(
            chat_id=chat_id,
            text="Well, it doesn't look like a valid phone number...")
        return None

    client = LOCAL_STORAGE[chat_id]
    client.auth_state = AuthStates.UNAUTHORIZED_STATE
    client.phone = update.message.contact.phone_number
    apt = auth.authenticate(client.phone)
    if apt == auth.NO_PHONE_FOUND:
        context.bot.send_message(
            chat_id=chat_id,
            text="User not found. Proceeding with authorization")
        context.bot.send_message(chat_id=chat_id,
                                 text="What building are you from?")
        return AuthStates.BUILDING_CHECKING_STATE

    context.bot.send_message(chat_id=chat_id,
                             text="Hey, I know you!")
    show_main_menu(update, context)
    return -1


def check_building(update, context):
    chat_id = update.effective_chat.id
    if not re.match(VALID_BUILDINGS, update.message.text):
        context.bot.send_message(chat_id=chat_id,
                                 text="Not sure it's a correct building...")
        return None

    LOCAL_STORAGE[chat_id].building = update.message.text
    context.bot.send_message(chat_id=chat_id,
                             text="What appartment are you from?")
    return AuthStates.APPARTMENT_CHECKING_STATE


def check_appartment(update, context):
    chat_id = update.effective_chat.id
    try:
        apt = int(update.message.text)
        if not (0 < apt < MAX_VALID_APPARTMENT):
            raise ValueError
    except ValueError:
        context.bot.send_message(chat_id=chat_id,
                                 text="Not sure it's a correct number...")
        return None

    LOCAL_STORAGE[chat_id].apt = apt
    context.bot.send_message(
        chat_id=chat_id,
        text="Last step: who is the owner of appartment?")
    return AuthStates.OWNER_FILLING_STATE


def fill_owner(update, context):
    chat_id = update.effective_chat.id
    LOCAL_STORAGE[chat_id].owner = update.message.text
    context.bot.send_message(
        chat_id=chat_id, text="I've asked request to serve you",
        reply_markup=InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(text="Check status",
                                 callback_data=CHECK_AUTH_VALUE)))
    return AuthStates.REQUEST_PENDING_STATE


def publish_request(update, context):
    chat_id = update.effective_chat.id
    # TODO: check status in the table
    if True:
        context.bot.send_message(
            chat_id=chat_id, text="Authorized",
            reply_markup=InlineKeyboardMarkup.from_row([]))
        LOCAL_STORAGE[chat_id].auth_state = AuthStates.AUTHORIZED_STATE
        show_main_menu(update, context)
        return -1


AUTHORIZE_ENTRANCE = CommandHandler('start', greeter)
AUTH_CONVERSATION_HANDLER = ConversationHandler(
    entry_points=[AUTHORIZE_ENTRANCE],
    states={
        AuthStates.PHONE_CHEKING_STATE:
            [MessageHandler(Filters.contact, got_contact)],
        AuthStates.BUILDING_CHECKING_STATE:
            [MessageHandler(Filters.text, check_building)],
        AuthStates.APPARTMENT_CHECKING_STATE:
            [MessageHandler(Filters.text, check_appartment)],
        AuthStates.OWNER_FILLING_STATE:
            [MessageHandler(Filters.text, fill_owner)],
        AuthStates.REQUEST_PENDING_STATE:
            [CallbackQueryHandler(publish_request, pattern=CHECK_AUTH_VALUE)]
    }, fallbacks=[AUTHORIZE_ENTRANCE], map_to_parent={
        AuthStates.UNAUTHORIZED_STATE: Flows.AUTHORIZATION,
        -1: Flows.MAIN_LOOP
    })

# TODO: actual map to parent:
# Entrance(AUTH) = Entrance(MAIN)
# Authorized(AUTH) = MainLoop(MAIN)
