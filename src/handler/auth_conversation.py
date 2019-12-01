import re

from telegram import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, \
    Filters, CallbackQueryHandler, Dispatcher

from config.config import VALID_HOUSES, MAX_VALID_APARTMENT
from src import AbstractDatabaseBridge
from src.common.const import *
from src.common.local_storage import Client
from src.common.tg_utils import send_typing_action
from src.handler.main_menu import show_main_menu

db: AbstractDatabaseBridge
dispatcher: Dispatcher


def __authorized(update, context):
    show_main_menu(update, context)
    dispatcher.add_handler(PEER_HANDLER)
    return -1


def request_is_still_active_message(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=AUTH_IN_PROGRESS,
        reply_markup=InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(
                text=CHECK_STATUS,
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
            text=f"{HI}, {update.effective_chat.first_name}")
        return __authorized(update, context)

    if db.is_pending(chat_id):
        return request_is_still_active_message(update, context)

    context.bot.send_message(
        chat_id=chat_id, text=GREETING_FIRST_TIME,
        reply_markup=ReplyKeyboardMarkup.from_row(
            [KeyboardButton(text=SHARE_PHONE_NUMBER,
                            request_contact=True)]))
    return AuthStates.PHONE_CHECKING_STATE


def request_contact(update, context):
    chat_id = update.effective_chat.id
    phone = re.sub(r'\D+', '', update.message.contact.phone_number)
    if not re.match(r'^[1-9][0-9]{10,}$', phone):
        context.bot.send_message(chat_id=chat_id, text=INVALID_PHONE_NUMBER)
        return None

    context.bot.send_message(chat_id=chat_id, text=LOOKING_FOR_YOU_IN_AUTH_DB,
                             reply_markup=ReplyKeyboardRemove())

    # TODO: cleanup database authorization
    client = Client.from_context(context)
    client.auth_state = AuthStates.UNAUTHORIZED_STATE
    client.phone = phone
    if not db.is_authorized(client.phone):
        context.bot.send_message(
            chat_id=chat_id, text=f'{CANNOT_FIND_YOU} {WHERE_ARE_YOU_FROM}')
        return AuthStates.HOUSE_CHECKING_STATE
    else:
        db.update_registered_chat_id(client.phone, chat_id)
        client.update_from_db(chat_id, db)

    context.bot.send_message(chat_id=chat_id, text=NO_AUTH_BUT_I_KNOW_NUMBER)
    return __authorized(update, context)


def check_house(update, context):
    chat_id = update.effective_chat.id
    house = update.message.text.strip()
    if not re.match(VALID_HOUSES, house):
        context.bot.send_message(chat_id=chat_id, text=INCORRECT_BUILDING)
        return None

    client = Client.from_context(context)
    client.house = house
    context.bot.send_message(chat_id=chat_id, text=WHAT_APT_ARE_YOU_FROM)
    return AuthStates.APARTMENT_CHECKING_STATE


def check_apartment(update, context):
    chat_id = update.effective_chat.id
    try:
        apt = int(update.message.text)
        if not (0 < apt < MAX_VALID_APARTMENT):
            raise ValueError
    except ValueError:
        context.bot.send_message(chat_id=chat_id, text=INCORRECT_APT)
        return None

    client = Client.from_context(context)
    client.apt = apt
    context.bot.send_message(chat_id=chat_id, text=AUTH_COMMENTS)
    return AuthStates.COMMEND_ADDING_STATE


def fill_owner(update, context):
    chat_id = update.effective_chat.id
    client = Client.from_context(context)
    db.new_registration(chat_id, client.phone, (client.house, client.apt),
                        update.message.text)
    context.bot.send_message(
        chat_id=chat_id, text=AUTH_PENDING_FIRST_MESSAGE,
        reply_markup=InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(
                text=CHECK_STATUS,
                callback_data=InlineQueriesCb.AUTH_CHECK.value)))

    try:
        buttons = [InlineKeyboardButton(text=text,
                                        callback_data=f"{cb.value};{chat_id}")
                   for text, cb in [(I_KNOW_THIS_PERSON,
                                     InlineQueriesCb.AUTH_CONFIRM),
                                    (I_DON_T_KNOW_THIS_PERSON,
                                     InlineQueriesCb.AUTH_REJECT)]]
        for peer_id in db.peers(chat_id, (client.house, client.apt)):
            context.bot.send_message(
                chat_id=peer_id,
                text=f"{client.phone} ({update.effective_chat.first_name}) "
                     f"{WANTS_TO_REGISTER_AT_YOUR_APT}",
                reply_markup=InlineKeyboardMarkup.from_column([buttons]))
    finally:
        pass

    return AuthStates.REQUEST_PENDING_STATE


@send_typing_action
def publish_request(update, context):
    if update.callback_query:
        update.callback_query.answer(text=CHECKING___)

    chat_id = update.effective_chat.id
    if db.is_authorized(chat_id):
        context.bot.send_message(chat_id=chat_id, text=AUTHORIZED)
        client = Client.from_context(context)
        client.auth_state = AuthStates.AUTHORIZED_STATE
        return __authorized(update, context)
    elif db.is_pending(chat_id):
        return request_is_still_active_message(update, context)
    else:
        context.bot.send_message(chat_id=chat_id, text=AUTH_REJECTED)
        return AuthStates.UNAUTHORIZED_STATE


def report_peer(update, _):
    update.callback_query.answer()
    data = update.callback_query.data.split(';')

    try:
        if data[0] == InlineQueriesCb.AUTH_CONFIRM.value:
            db.peer_confirm(data[1])
        else:
            db.peer_reject(data[1])
    finally:
        pass


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
        AuthStates.PHONE_CHECKING_STATE:
            [MessageHandler(Filters.contact, request_contact)],
        AuthStates.HOUSE_CHECKING_STATE:
            [MessageHandler(Filters.text, check_house)],
        AuthStates.APARTMENT_CHECKING_STATE:
            [MessageHandler(Filters.text, check_apartment)],
        AuthStates.COMMEND_ADDING_STATE:
            [MessageHandler(Filters.text, fill_owner)],
        AuthStates.REQUEST_PENDING_STATE:
            [CallbackQueryHandler(
                publish_request,
                pattern=f"^{InlineQueriesCb.AUTH_CHECK.value}$")]
    }, fallbacks=[AUTHORIZE_ENTRANCE], map_to_parent={
        AuthStates.UNAUTHORIZED_STATE: Flows.AUTHORIZATION,
        -1: Flows.MAIN_LOOP
    })
