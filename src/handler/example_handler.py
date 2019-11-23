import json
import re
from collections import defaultdict
from enum import Enum, auto, unique

from statemachine import StateMachine, State
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, \
    InlineKeyboardMarkup, InlineKeyboardButton

from Authenticator import Authenticator, SAMPLE_DB
from config.config import VALID_BUILDINGS, MAX_VALID_APPARTMENT
from src import REGISTERED_BRIDGES
from src.gdrive import test_get_request

db = None
config = json.loads(open('config/db.json').read())
bridge_type = config.pop('type')


for bridge in REGISTERED_BRIDGES:
    if bridge.responds_to(bridge_type):
        db = bridge(config)
        break
else:
    raise LookupError(f"No bridge found for {bridge_type}")


GREETING_FIRST_TIME = "Hey, I'm a bot. You are not authorized, give me your " \
                      "phone number, boots and motorcycle"
GREETING_AUTH = "Hey, <username>"

START_AUTHORIZED = True


@unique
class InquiryType(Enum):
    FAQ_CB = auto()
    MY_REQUESTS_CB = auto()
    NEW_REQUEST_CB = auto()
    CHECK_AUTHORIZATION_CB = auto()


class AuthorizationSession:
    class AuthStateMachine(StateMachine):
        unauthorized = State('unauth', initial=True)
        building_check = State('building check')
        apt_check = State('appartment check')
        request_pending = State('pending')
        authorized = State('authorized')

        init_registration = unauthorized.to(building_check)
        verify_building = building_check.to(apt_check)
        verify_appartment = apt_check.to(request_pending)
        authorize = request_pending.to(authorized)

    def __init__(self, state='unauthorized'):
        self.state = state
        self.building = ""
        self.apt = 0
        self.sm = self.AuthStateMachine(self)
        self.sm.verify_building.validators.append(self.validate_building)
        self.sm.verify_appartment.validators.append(self.validate_apt)

    def start_registration(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="What is your building?")
        try:
            self.sm.init_registration()
        finally:
            pass

    def validate_building(self):
        assert re.match(VALID_BUILDINGS, self.building)

    def validate_apt(self):
        assert 0 < self.apt < MAX_VALID_APPARTMENT

    def authorization_finished(self, update, context):
        authorized = START_AUTHORIZED
        try:
            if self.sm.is_authorized:
                authorized = True
            elif self.sm.is_unauthorized:
                self.start_registration(update, context)
            elif self.sm.is_building_check:
                self.building = update.effective_message.text
                self.sm.verify_building()
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="What is your appartment?")
            elif self.sm.is_apt_check:
                self.apt = int(update.effective_message.text)
                self.sm.verify_appartment()
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="What is the name of the owner?")
            elif self.sm.is_request_pending:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Authorization pending",
                    reply_markup=InlineKeyboardMarkup.from_button(
                        InlineKeyboardButton(
                            text="Check",
                            callback_data=
                            InquiryType.CHECK_AUTHORIZATION_CB.value)))
        finally:
            return authorized


    @staticmethod
    def factory():
        return AuthorizationSession()


class InquiryHandler:
    @classmethod
    def handle_inquiry(cls, update, context):
        if update.callback_query.data == InquiryType.FAQ_CB.value:
            pass  # TODO: show FAQ menu
        elif update.callback_query.data == InquiryType.MY_REQUESTS_CB.value:
            pass  # TODO: show user requests
        elif update.callback_query.data == InquiryType.NEW_REQUEST_CB.value:
            pass  # TODO: start new request flow
        elif update.callback_query.data == InquiryType.CHECK_AUTHORIZATION_CB.value:
            # TODO
            local_mem[update.effective_chat.id].sm.authorize()
            context.bot.send_message(
                chat_id=update.effective_chat.id, text="Authorized.",
                reply_markup=InlineKeyboardMarkup.from_row([]))
        # TODO: implement callbackdata handling
        # next line is temp!
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Your callback data: {update.callback_query.data}, your chat id: {update.effective_chat.id}',
            reply_markup=InlineKeyboardMarkup.from_row([])
        )

    @classmethod
    def show_menu(cls, update, context):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Main menu",
            reply_markup=InlineKeyboardMarkup.from_row(
                [InlineKeyboardButton(
                     text="FAQ", callback_data=InquiryType.FAQ_CB.value),
                 InlineKeyboardButton(
                     text="My opened requests",
                     callback_data=InquiryType.MY_REQUESTS_CB.value),
                 InlineKeyboardButton(
                     text="Create new request",
                     callback_data=InquiryType.NEW_REQUEST_CB.value)]))


auth = Authenticator(SAMPLE_DB)
local_mem = defaultdict(AuthorizationSession.factory)  # { chatId: { AuthorizationSession, other classes } }


def start(update, context):
    auth_session = local_mem[update.effective_chat.id]

    if auth_session.authorization_finished(update, context):
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=GREETING_AUTH)
        InquiryHandler.show_menu(update, context)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=GREETING_FIRST_TIME,
            reply_markup=ReplyKeyboardMarkup.from_row(
                [KeyboardButton(text="Share phone number", request_contact=True)],
                one_time_keyboard=True))



def echo(update, context):
    if not local_mem[update.effective_chat.id].\
            authorization_finished(update, context):
        return

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Authorized. Mirroring: " +
                             update.message.text)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Sorry, I didn't understand that command.")


def got_contact(update, context):
    # TODO: Check we are actually in authorization process

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Checking for authorization",
        reply_markup=ReplyKeyboardRemove())
    # TODO: actual check
    apt = auth.authenticate(update.message.contact.phone_number)
    if apt == auth.NO_PHONE_FOUND:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="User not found. Proceeding with authorization")
        local_mem[update.effective_chat.id].\
            start_registration(update, context)
    else:
        InquiryHandler.show_menu(update, context)


def got_callback(update, context):
    InquiryHandler.handle_inquiry(update, context)


def test_gdrive(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=test_get_request())


def try_authorize(update, context):
    # TODO: Attach contact info
    is_authorized = db.is_authorized_contact()
    response = 'Welcome' if is_authorized else "You're not welcomed here"

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=response)
