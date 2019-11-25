from enum import unique, Enum, auto

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler

from src.handler.const import Flows, TicketsCategories


@unique
class MainMenuOptions(Enum):
    FAQ = auto()
    MY_REQUESTS = auto()
    NEW_REQUEST = auto()


_SELECTOR = {
    MainMenuOptions.FAQ.value: Flows.MAIN_LOOP,
    MainMenuOptions.MY_REQUESTS.value: Flows.LIST_TICKETS,
    MainMenuOptions.NEW_REQUEST.value: Flows.NEW_TICKET,
}

CANCEL_BUTTON_VALUE = 'Cancel'


def show_main_menu(update, context):
    if update.callback_query:
        update.callback_query.answer()

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Main menu",
        reply_markup=InlineKeyboardMarkup.from_row(
            [InlineKeyboardButton(
                 text="FAQ", callback_data=MainMenuOptions.FAQ.value),
             InlineKeyboardButton(
                 text="My opened requests",
                 callback_data=MainMenuOptions.MY_REQUESTS.value),
             InlineKeyboardButton(
                 text="Create new request",
                 callback_data=MainMenuOptions.NEW_REQUEST.value)]))


def new_ticket_menu(update, context):
    table = []
    for i, c in enumerate(list(TicketsCategories)):
        if i % 3 == 0:
            table.append([])
        table[-1].append(InlineKeyboardButton(text=c.value,
                                              callback_data=c.value))
    table.append([InlineKeyboardButton(text="Cancel",
                                       callback_data=CANCEL_BUTTON_VALUE)])
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
        choice = _SELECTOR.get(int(update.callback_query.data))
        if choice:
            menu = _SUBMENU.get(choice)
            if menu:
                menu(update, context)

            return choice
    finally:
        pass

    return -1


MAIN_MENU_HANDLER = CallbackQueryHandler(handle_main_menu)