from typing import Tuple, Dict

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler, Dispatcher

from src import AbstractDatabaseBridge
from src.db.base import TicketData
from src.handler.const import *
from src.handler.local_storage import Client
from tg_utils import send_typing_action, TICKET_CMD, CommandPrefixHandler, \
    ticket_link

dispatcher: Dispatcher
db: AbstractDatabaseBridge
__added_ticket_command = False


class TicketsHandler(CommandPrefixHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            sep='_',
            suffix_checker=lambda l: len(l) == 1 and l[0].isdigit,
            **kwargs)


def __ticket_formatter(ticket: Tuple[TicketData, Dict]) -> str:
    s = f"Заявка {ticket_link(ticket[1]['id'])} " \
        f"({ticket[1]['date_text']} {ticket[1]['time_text']}): " \
        f"{ticket[1]['status']}\n" \
        f"Категорія: {ticket[0].category}\n" \
        f"Опис: {ticket[0].description}\n"

    if ticket[1]['comments']: \
        s += f"Коментарі виконавця: {ticket[1]['comments']}"

    return s


@send_typing_action
def get_ticket_info(update, context):
    chat_id = update.effective_chat.id
    try:
        if not context.args or len(context.args) != 1:
            raise RuntimeError
        ticket_id = int(context.args[0])
    except (ValueError, RuntimeError):
        context.bot.send_message(chat_id=chat_id,
                                 text=NEED_PROPER_TICKET_COMMAND_FORMAT)
        return None

    context.bot.send_message(
        chat_id=chat_id,
        text=__ticket_formatter(db.get_ticket_details(ticket_id)))


@send_typing_action
def show_tickets(update, context):
    client = Client.from_context(context)
    for ticket in db.tickets((client.house, client.apt)):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=__ticket_formatter(ticket))


@send_typing_action
def show_faq(update, context):
    pass


def show_main_menu(update, context):
    if update.callback_query:
        update.callback_query.answer()

    if not __added_ticket_command:
        #dispatcher.add_handler(CommandHandler(TICKET_CMD, get_ticket_info))
        dispatcher.add_handler(TicketsHandler(command=TICKET_CMD,
                                              callback=get_ticket_info))

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=MENU_TITLE,
        reply_markup=InlineKeyboardMarkup.from_column(
            [InlineKeyboardButton(
                text=FAQ_TITLE,
                callback_data=InlineQueriesCb.MENU_FAQ.value),
             InlineKeyboardButton(
                text=SHOW_MY_REQUESTS,
                callback_data=InlineQueriesCb.MENU_MY_OPEN_TICKETS.value),
             InlineKeyboardButton(
                text=CREATE_NEW_TICKET,
                callback_data=InlineQueriesCb.MENU_NEW_TICKET.value)]))


def new_ticket_menu(update, context):
    if update.callback_query:
        update.callback_query.answer()

    table = []
    for i, c in enumerate(list(TicketsCategories)):
        if i % 3 == 0:
            table.append([])
        table[-1].append(InlineKeyboardButton(text=c.value,
                                              callback_data=c.value))
    table.append([InlineKeyboardButton(
        text=InlineQueriesCb.TICKET_CANCEL.value,
        callback_data=InlineQueriesCb.TICKET_CANCEL.value)])
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=SELECT_TICKET_CATEGORY,
        reply_markup=InlineKeyboardMarkup(table))


def handle_main_menu(update, context):
    if update.callback_query:
        update.callback_query.answer()

    choice = update.callback_query.data
    if choice == InlineQueriesCb.MENU_FAQ.value:
        show_faq(update, context)
    elif choice == InlineQueriesCb.MENU_MY_OPEN_TICKETS.value:
        show_tickets(update, context)
    elif choice == InlineQueriesCb.MENU_NEW_TICKET.value:
        new_ticket_menu(update, context)
        return Flows.NEW_TICKET


MAIN_MENU_HANDLER = CallbackQueryHandler(handle_main_menu)
