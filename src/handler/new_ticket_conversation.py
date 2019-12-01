import os
import shutil
from datetime import datetime
from tempfile import mkdtemp

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, \
    CallbackQueryHandler, MessageHandler, Filters

from src import AbstractDatabaseBridge
from src.common.const import *
from src.common.local_storage import Client, ticket_from_context
from src.common.tg_utils import send_typing_action, ticket_link
from src.common.ticket import TicketData
from src.handler.main_menu import show_main_menu

db: AbstractDatabaseBridge


def __finish_markup():
    return InlineKeyboardMarkup.from_row(
        [InlineKeyboardButton(text=e.value, callback_data=e.value)
         for e in [InlineQueriesCb.TICKET_STOP,
                   InlineQueriesCb.TICKET_CANCEL]]
    )


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
        + TO_CANCEL_USE + f"{InlineQueriesCb.TICKET_CANCEL.value}",
        reply_markup=__finish_markup())
    return NewTicketStates.ENTERING_DESCRIPTION


def enter_description(update, context):
    # TODO: too much text check
    ticket_from_context(context)['messages'].append(update.message.text)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=ADD_MORE_DESCRIPTION,
        reply_markup=__finish_markup())


def add_photo(update, context):
    chat_id = update.effective_chat.id
    ticket = ticket_from_context(context)
    if not ticket['media_dir']:
        ticket['media_dir'] = mkdtemp(suffix=f'_{chat_id}')

    acceptable_photo = max(update.message.photo,
                           key=lambda x:
                           x['file_size']
                           if x['file_size'] < MAX_PHOTO_SIZE
                           else -1)
    if acceptable_photo['file_size'] > MAX_PHOTO_SIZE:
        acceptable_photo = min(update.message.photo,
                               key=lambda x: x['file_size'])
    file = acceptable_photo.get_file()
    path = os.path.join(ticket['media_dir'], os.path.basename(file.file_path))
    ticket['media'].append(file.download(path))
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=UPLOADING_SINGLE_PHOTO + ADD_MORE_DESCRIPTION,
        reply_markup=__finish_markup())


@send_typing_action
def description_stop_handler(update, context):
    chat_id = update.effective_chat.id

    if update.callback_query.data == InlineQueriesCb.TICKET_CANCEL.value:
        return cancel(update, context)

    update.callback_query.answer()

    client = Client.from_context(context)
    ticket = ticket_from_context(context)

    # TODO: save message ids and fetch data from edited messages
    combined_message = "\n".join([m for m in ticket['messages']])
    if not combined_message.strip():
        context.bot.send_message(chat_id=chat_id,
                                 text=CANNOT_CREATE_TICKET_WITH_NO_DESCRIPTION)
        return None

    _id = db.new_ticket(TicketData(
        chat_id=chat_id,
        phone=client.phone,
        address=(client.house, client.apt),
        datetime=datetime.now(),
        category=ticket['category'],
        description=combined_message,
        media='+' if ticket['media'] else ''
    ))

    try:
        context.bot.send_message(chat_id=chat_id, text=UPLOADING_PHOTOS)
        db.save_artifacts(_id, {f: os.path.basename(f)
                                for f in ticket['media']})
        shutil.rmtree(ticket['media_dir'], ignore_errors=True)
        context.bot.send_message(chat_id=chat_id, text=UPLOADED_PHOTOS)
    except RuntimeError:
        context.bot.send_message(chat_id=chat_id,
                                 text=CANNOT_SAVE_PHOTOS)

    # TODO: provide id as a hook for check
    context.bot.send_message(
        chat_id=chat_id,
        text=I_OPENED_A_TICKET + USE_A_COMMAND_TO_CHECK + ticket_link(_id))

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
