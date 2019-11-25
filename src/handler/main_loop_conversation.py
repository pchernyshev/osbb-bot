from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler

from src.handler.const import Flows, TicketsCategories, InlineQueriesCb

_SELECTOR = {
    InlineQueriesCb.MENU_FAQ.value: Flows.MAIN_LOOP,
    InlineQueriesCb.MENU_MY_REQUESTS.value: Flows.LIST_TICKETS,
    InlineQueriesCb.MENU_NEW_REQUEST.value: Flows.NEW_TICKET,
}


def show_main_menu(update, context):
    if update.callback_query:
        # try:
        #     update.callback_query.edit_message_reply_markup(
        #         reply_markup=InlineKeyboardMarkup([[]]))
        # finally:
        #     pass
        update.callback_query.answer()

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Main menu",
        reply_markup=InlineKeyboardMarkup.from_row(
            [InlineKeyboardButton(
                 text="FAQ", callback_data=InlineQueriesCb.MENU_FAQ.value),
             InlineKeyboardButton(
                 text="My opened requests",
                 callback_data=InlineQueriesCb.MENU_MY_REQUESTS.value),
             InlineKeyboardButton(
                 text="Create new request",
                 callback_data=InlineQueriesCb.MENU_NEW_REQUEST.value)]))


def new_ticket_menu(update, context):
    if update.callback_query:
        # try:
        #     update.callback_query.edit_message_reply_markup(
        #         reply_markup=InlineKeyboardMarkup([[]]))
        # finally:
        #     pass
        update.callback_query.answer()

    table = []
    for i, c in enumerate(list(TicketsCategories)):
        if i % 3 == 0:
            table.append([])
        table[-1].append(InlineKeyboardButton(text=c.value,
                                              callback_data=c.value))
    table.append([InlineKeyboardButton(
        text="Cancel", callback_data=InlineQueriesCb.TICKET_CANCEL.value)])
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Select relevant category",
        reply_markup=InlineKeyboardMarkup(table))


_SUBMENU = {
    Flows.MAIN_LOOP: show_main_menu,
    Flows.LIST_TICKETS: None,
    Flows.NEW_TICKET: new_ticket_menu
}


def handle_main_menu(update, context):
    try:
        if update.callback_query:
            update.callback_query.answer()
        choice = _SELECTOR.get(update.callback_query.data)
        if choice:
            menu = _SUBMENU.get(choice)
            if menu:
                menu(update, context)

            return choice
    finally:
        pass

    return -1


MAIN_MENU_HANDLER = CallbackQueryHandler(handle_main_menu)