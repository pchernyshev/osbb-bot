from datetime import datetime

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, CommandHandler, \
    CallbackQueryHandler, MessageHandler, Filters

from src import AbstractDatabaseBridge
from src.db.base import TicketData
from src.handler.const import NewTicketStates, Flows, InlineQueriesCb
from src.handler.local_storage import Client
from src.handler.main_loop_conversation import show_main_menu, \
    new_ticket_menu

# TODO: move to context
db: AbstractDatabaseBridge
TicketsInProgress = dict()


def select_category(update, context):
    # try:
    #     update.callback_query.edit_message_reply_markup(
    #         reply_markup=InlineKeyboardMarkup([[]]))
    # finally:
    #     pass
    if update.callback_query.data == InlineQueriesCb.TICKET_CANCEL.value:
        return cancel(update, context)

    update.callback_query.answer()
    TicketsInProgress[update.effective_chat.id] = {
        'category': update.callback_query.data,
        'messages': [],
        'media': []
    }

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Please add description. Attach photos, if necessary. "
             "Click stop to finalize and New for another one.",
        reply_markup=InlineKeyboardMarkup.from_row([
            InlineKeyboardButton(text="Stop",
                                 callback_data=InlineQueriesCb.TICKET_STOP.value),
            InlineKeyboardButton(text="New",
                                 callback_data=InlineQueriesCb.TICKET_NEW.value),
            InlineKeyboardButton(text="Cancel ticket",
                                 callback_data=InlineQueriesCb.TICKET_CANCEL.value)]))
    return NewTicketStates.ENTERING_DESCRIPTION


def enter_description(update, context):
    # TODO: too much text check
    TicketsInProgress[update.effective_chat.id]['messages'].\
        append(update.message.text)


def add_photo(update, context):
    #context.bot.send_message(chat_id=update.effective_chat.id,
    #                         text=f"Yay, photo!")
    # update.message.effective_attachment
    TicketsInProgress[update.effective_chat.id]['media']. \
        append(update.message.photo)


def description_stop_handler(update, context):
    chat_id = update.effective_chat.id

    if update.callback_query.data == InlineQueriesCb.TICKET_CANCEL.value:
        update.callback_query.answer(text="Ticket creation canceled")
        return cancel(update, context)

    client = Client.get_client_from_context(context)
    if not client.is_valid():
        client.update_from_db(chat_id, db)
    if not client.is_valid():
        update.callback_query.answer(text="Ticket creation canceled")
        cancel(update, context)

    update.callback_query.answer()

    current_input = TicketsInProgress[chat_id]
    combined_message = "\n".join([m for m in current_input['messages']])

    context.bot.send_message(
        chat_id=chat_id,
        text=f"You entered {combined_message}")
    if current_input['media']:
        # TODO: bot.get_file() and attach somewhere
        context.bot.send_message(
            chat_id=chat_id,
            text="... and attached some photos")

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
        text=f"Here is your new ticket ID #{_id}")

    if update.callback_query.data == InlineQueriesCb.TICKET_NEW.value:
        new_ticket_menu(update, context)
        return NewTicketStates.SELECTING_CATEGORY

    cancel(update, context)


def cancel(update, context):
    if update.callback_query:
        update.callback_query.answer()

    show_main_menu(update, context)
    return -1


_CANCEL_COMMAND = CommandHandler('cancel', cancel)
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
    }, fallbacks=[_CANCEL_COMMAND], map_to_parent={
        -1: Flows.MAIN_LOOP
    }
)