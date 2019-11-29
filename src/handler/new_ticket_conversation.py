from datetime import datetime

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, \
    CallbackQueryHandler, MessageHandler, Filters

from src import AbstractDatabaseBridge
from src.common.const import *
from src.common.local_storage import Client, ticket_from_context
from src.common.tg_utils import send_typing_action, ticket_link
from src.common.ticket import TicketData
from src.handler.main_menu import show_main_menu, \
    new_ticket_menu

db: AbstractDatabaseBridge


def select_category(update, context):
    if update.callback_query.data == InlineQueriesCb.TICKET_CANCEL.value:
        return cancel(update, context)

    update.callback_query.answer()
    current_ticket = ticket_from_context(context, new_ticket=True)
    current_ticket['category'] = update.callback_query.data

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=PLEASE_DESCRIBE_A_PROBLEM
        + TO_FINISH_USE + f"{InlineQueriesCb.TICKET_STOP.value}.\n"
        + TO_CANCEL_USE + f"{InlineQueriesCb.TICKET_CANCEL.value}\n"
        + TO_ADD_ANOTHER_ONE_USE + f"{InlineQueriesCb.TICKET_NEW.value}",
        reply_markup=InlineKeyboardMarkup.from_row(
            [InlineKeyboardButton(text=e.value, callback_data=e.value)
             for e in [InlineQueriesCb.TICKET_STOP,
                       InlineQueriesCb.TICKET_NEW,
                       InlineQueriesCb.TICKET_CANCEL]]
        ))
    return NewTicketStates.ENTERING_DESCRIPTION


def enter_description(update, context):
    # TODO: too much text check
    ticket_from_context(context)['messages'].append(update.message.text)


def add_photo(update, context):
    # TODO: size check + update.message.effective_attachment
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=CANNOT_SAVE_PHOTOS)
    # Use ticket_from_context(context)['media'].append(update.message.photo)


@send_typing_action
def description_stop_handler(update, context):
    chat_id = update.effective_chat.id

    if update.callback_query.data == InlineQueriesCb.TICKET_CANCEL.value:
        return cancel(update, context)

    update.callback_query.answer()

    client = Client.from_context(context)
    current_input = ticket_from_context(context)

    # TODO: save message ids and fetch data from edited messages
    combined_message = "\n".join([m for m in current_input['messages']])
    if not combined_message.strip():
        context.bot.send_message(chat_id=chat_id,
                                 text=CANNOT_CREATE_TICKET_WITH_NO_DESCRIPTION)
        return None

    _id = db.new_ticket(TicketData(
        chat_id=chat_id,
        phone=client.phone,
        address=(client.house, client.apt),
        datetime=datetime.now(),
        category=current_input['category'],
        description=combined_message,
        media=""
    ))

    # TODO: provide id as a hook for check
    context.bot.send_message(
        chat_id=chat_id,
        text=I_OPENED_A_TICKET + USE_A_COMMAND_TO_CHECK + ticket_link(_id))

    if update.callback_query.data == InlineQueriesCb.TICKET_NEW.value:
        new_ticket_menu(update, context)
        return NewTicketStates.SELECTING_CATEGORY

    return done(update, context)


def done(update, context):
    show_main_menu(update, context)
    return -1


def cancel(update, context):
    if update.callback_query:
        update.callback_query.answer(text=CANCEL_NEW_TICKET)
    return done(update, context)


SELECT_HANDLER = CallbackQueryHandler(select_category)
NEW_TICKET_CONVERSATION = ConversationHandler(
    entry_points=[SELECT_HANDLER],
    states={
        NewTicketStates.SELECTING_CATEGORY: [SELECT_HANDLER],
        NewTicketStates.ENTERING_DESCRIPTION: [
            MessageHandler(Filters.text, enter_description),
            MessageHandler(Filters.photo, add_photo),
            CallbackQueryHandler(description_stop_handler)
        ],
    },
    fallbacks=[CallbackQueryHandler(cancel)],
    map_to_parent={-1: Flows.MAIN_LOOP})
# TODO: organize fallbacks
