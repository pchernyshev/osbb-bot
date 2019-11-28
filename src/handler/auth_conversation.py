import re

from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, \
    Filters, CallbackQueryHandler

from config.config import VALID_HOUSES, MAX_VALID_APARTMENT
from src import AbstractDatabaseBridge
from src.handler.const import AuthStates, Flows, InlineQueriesCb
from src.handler.local_storage import Client
from src.handler.main_loop_conversation import show_main_menu

GREETING_FIRST_TIME = "Hey, I'm a bot. You are not authorized, give me your " \
                      "phone number, boots and motorcycle"

db: AbstractDatabaseBridge


def request_is_still_active_message(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I have a pending registration request for you."
             "It's still in progress",
        reply_markup=InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(text="Check status",
                                 callback_data=InlineQueriesCb.AUTH_CHECK.value)))
    return AuthStates.REQUEST_PENDING_STATE


def greeter(update, context):
    chat_id = update.effective_chat.id
    client = Client.from_context(context)
    if not client.is_valid():
        client.update_from_db(chat_id, db)

    if client.auth_state == AuthStates.AUTHORIZED_STATE:
        context.bot.send_message(
            chat_id=chat_id,
            text=f"Hi, {update.effective_chat.first_name}")
        show_main_menu(update, context)
        return -1

    if db.is_pending(chat_id):
        return request_is_still_active_message(update, context)

    context.bot.send_message(
        chat_id=chat_id, text=GREETING_FIRST_TIME,
        reply_markup=ReplyKeyboardMarkup.from_row(
            [KeyboardButton(text="Share phone number",
                            request_contact=True)]))
    return AuthStates.PHONE_CHEKING_STATE


def request_contact(update, context):
    chat_id = update.effective_chat.id
    phone = re.sub(r'\D+', '', update.message.contact.phone_number)
    if not re.match(r'^[1-9][0-9]{10,}$', phone):
        context.bot.send_message(
            chat_id=chat_id,
            text="Well, it doesn't look like a valid phone number...")
        return None

    context.bot.send_message(chat_id=chat_id,
                             text="Looking for you in database",
                             reply_markup=ReplyKeyboardRemove())

    # TODO: cleanup database authorization
    client = Client.from_context(context)
    client.auth_state = AuthStates.UNAUTHORIZED_STATE
    client.phone = phone
    if not db.is_authorized(client.phone):
        context.bot.send_message(
            chat_id=chat_id,
            text="I cannot find you. What building are you from?")
        return AuthStates.HOUSE_CHECKING_STATE

    db.update_registered_chat_id(client.phone, chat_id)
    context.bot.send_message(
        chat_id=chat_id,
        text="I know you, though we never talked before. Welcome!")
    show_main_menu(update, context)
    return -1


def check_house(update, context):
    chat_id = update.effective_chat.id
    if not re.match(VALID_HOUSES, update.message.text):
        context.bot.send_message(chat_id=chat_id,
                                 text="Not sure it's a correct building...")
        return None

    client = Client.from_context(context)
    client.house = update.message.text
    context.bot.send_message(chat_id=chat_id,
                             text="What apartment are you from?")
    return AuthStates.APARTMENT_CHECKING_STATE


def check_apartment(update, context):
    chat_id = update.effective_chat.id
    try:
        apt = int(update.message.text)
        if not (0 < apt < MAX_VALID_APARTMENT):
            raise ValueError
    except ValueError:
        context.bot.send_message(chat_id=chat_id,
                                 text="Not sure it's a correct number...")
        return None

    client = Client.from_context(context)
    client.apt = apt
    context.bot.send_message(
        chat_id=chat_id,
        text="Last step: who is the owner of apartment?")
    return AuthStates.OWNER_FILLING_STATE


def fill_owner(update, context):
    chat_id = update.effective_chat.id
    client = Client.from_context(context)
    db.new_registration(chat_id, client.phone, (client.house, client.apt),
                        update.message.text)
    context.bot.send_message(
        chat_id=chat_id, text="I've asked request to serve you",
        reply_markup=InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(text="Check status",
                                 callback_data=InlineQueriesCb.AUTH_CHECK.value)))

    try:
        for peer_id in db.peers(chat_id, (client.house, client.apt)):
            context.bot.send_message(
                chat_id=peer_id,
                text=f"{client.phone} is registering at your apartment",
                reply_markup=InlineKeyboardMarkup.from_column([
                    InlineKeyboardButton(
                        text="It's ok, I know this person",
                        callback_data=f"{InlineQueriesCb.AUTH_CONFIRM.value};{chat_id}"),
                    InlineKeyboardButton(
                        text="I don't know this person",
                        callback_data=f"{InlineQueriesCb.AUTH_REJECT.value};{chat_id}"),
                ])
            )
            # TODO: Ask p to confirm
    finally:
        pass

    return AuthStates.REQUEST_PENDING_STATE


def publish_request(update, context):
    if update.callback_query:
        update.callback_query.answer(text="Checking...")

    chat_id = update.effective_chat.id
    if db.is_authorized(chat_id):
        context.bot.send_message(chat_id=chat_id, text="Authorized")
        client = Client.from_context(context)
        client.auth_state = AuthStates.AUTHORIZED_STATE
        show_main_menu(update, context)
        return -1
    else:
        if db.is_pending(chat_id):
            return request_is_still_active_message(update, context)

        context.bot.send_message(
            chat_id=chat_id,
            text="It seems your authorization was rejected. Sorry about it.\n"
                 "You may want to start from begginning with /start command")
        return AuthStates.UNAUTHORIZED_STATE


def report_peer(update, context):
    update.callback_query.answer()
    data = update.callback_query.data.split(';')

    # if data[0] not in (InlineQueriesCb.AUTH_CONFIRM.value,
    #                    InlineQueriesCb.AUTH_REJECT.value):
    #     return

    if data[0] == InlineQueriesCb.AUTH_CONFIRM.value:
        db.peer_confirm(data[1])
    else:
        db.peer_reject(data[1])


AUTHORIZE_ENTRANCE = CommandHandler('start', greeter)
PEER_HANDLER = CallbackQueryHandler(
    report_peer,
    pattern=f"^(?:{InlineQueriesCb.AUTH_CONFIRM.value}|"
            f"{InlineQueriesCb.AUTH_REJECT.value});\\d+$")
AUTH_CONVERSATION_HANDLER = ConversationHandler(
    entry_points=[AUTHORIZE_ENTRANCE],
    states={
        AuthStates.UNAUTHORIZED_STATE:
            [AUTHORIZE_ENTRANCE],
        AuthStates.PHONE_CHEKING_STATE:
            [MessageHandler(Filters.contact, request_contact)],
        AuthStates.HOUSE_CHECKING_STATE:
            [MessageHandler(Filters.text, check_house)],
        AuthStates.APARTMENT_CHECKING_STATE:
            [MessageHandler(Filters.text, check_apartment)],
        AuthStates.OWNER_FILLING_STATE:
            [MessageHandler(Filters.text, fill_owner)],
        AuthStates.REQUEST_PENDING_STATE:
            [CallbackQueryHandler(
                publish_request,
                pattern=f"^{InlineQueriesCb.AUTH_CHECK.value}$")]
    }, fallbacks=[AUTHORIZE_ENTRANCE], map_to_parent={
        AuthStates.UNAUTHORIZED_STATE: Flows.AUTHORIZATION,
        -1: Flows.MAIN_LOOP
    })

# TODO: actual map to parent:
# Entrance(AUTH) = Entrance(MAIN)
# Authorized(AUTH) = MainLoop(MAIN)
