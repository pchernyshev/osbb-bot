from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler, Dispatcher

from src import AbstractDatabaseBridge
from src.common.const import *
from src.common.local_storage import Client
from src.common.tg_utils import send_typing_action, TICKET_CMD, \
    CommandPrefixHandler, ticket_link
from src.common.ticket import ticket_formatter, ticket_status, ticket_id

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
        text=ticket_formatter(db.get_ticket_details(ticket_id)))


@send_typing_action
def show_tickets(update, context):
    client = Client.from_context(context)
    closed = []
    found = False
    for ticket in db.tickets((client.house, client.apt)):
        if ticket_status(ticket) != TicketStatesStr.DONE.value:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=ticket_formatter(ticket))
            found = True
        else:
            closed.append(ticket_id(ticket))

    if not found:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=I_HAVE_NO_TICKETS_OPENED_BY_YOU)
        if closed:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"{I_HAVE_CLOSED_TICKETS}: " +
                '\n'.join([ticket_link(_id) for _id in closed]))


@send_typing_action
def show_faq(update, context):
    for n, (q, a) in enumerate(db.fetch_faq(), 1):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'{n}. {q}\n{a}\n')


def show_main_menu(update, context):
    if update.callback_query:
        update.callback_query.answer()

    if not __added_ticket_command:
        dispatcher.add_handler(TicketsHandler(
            command=TICKET_CMD, callback=get_ticket_info))

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
    # noinspection PyTypeChecker
    for i, c in enumerate(TicketsCategories):
        if i % CATEGORIES_IN_A_ROW == 0:
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
        show_main_menu(update, context)
    elif choice == InlineQueriesCb.MENU_MY_OPEN_TICKETS.value:
        show_tickets(update, context)
        show_main_menu(update, context)
    elif choice == InlineQueriesCb.MENU_NEW_TICKET.value:
        new_ticket_menu(update, context)
        return Flows.NEW_TICKET


MAIN_MENU_HANDLER = CallbackQueryHandler(handle_main_menu)
