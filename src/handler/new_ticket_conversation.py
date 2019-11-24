from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, CommandHandler, \
    CallbackQueryHandler, MessageHandler, Filters

from src.handler.const import NewTicketStates, Flows
from src.handler.main_loop_conversation import show_main_menu, \
    CANCEL_BUTTON_VALUE, new_ticket_menu

STOP_BUTTON_VALUE = 'Stop'
NEW_BUTTON_VALUE = 'New'


def select_category(update, context):
    if update.callback_query.data == CANCEL_BUTTON_VALUE:
        return cancel(update, context)

    # TODO: save somewhere category
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Please add description. Attach photos, if necessary. "
             "Click stop to finalize and New for another one.",
        reply_markup=InlineKeyboardMarkup.from_row([
            InlineKeyboardButton(text="Stop",
                                 callback_data=STOP_BUTTON_VALUE),
            InlineKeyboardButton(text="New",
                                 callback_data=NEW_BUTTON_VALUE),
            InlineKeyboardButton(text="Cancel ticket",
                                 callback_data=CANCEL_BUTTON_VALUE)]))
    return NewTicketStates.ENTERING_DESCRIPTION


def enter_description(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"You entered {update.message.text}")
    # TODO: save messages


def add_photo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Yay, photo!")
    # TODO: save photos


def description_stop_handler(update, context):
    if update.callback_query.data == CANCEL_BUTTON_VALUE:
        return cancel(update, context)

    _id = "TICKET_ID"
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Here is your {_id}",
        reply_markup=InlineKeyboardMarkup([]))

    if update.callback_query.data == NEW_BUTTON_VALUE:
        new_ticket_menu(update, context)
        return NewTicketStates.SELECTING_CATEGORY

    cancel(update, context)


def cancel(update, context):
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