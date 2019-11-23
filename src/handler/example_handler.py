import json

from statemachine import StateMachine, State
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, replymarkup

from Authenticator import Authenticator, SAMPLE_DB

from src import REGISTERED_BRIDGES

db = None
# config = json.loads(open('config/db.json').read())
# bridge_type = config.pop('type')
#
#
# for bridge in REGISTERED_BRIDGES:
#     if bridge.responds_to(bridge_type):
#         db = bridge(config)
#         break
# else:
#     raise LookupError(f"No bridge found for {bridge_type}")


GREETING_FIRST_TIME = "Hey, I'm a bot. You are not authorized, give me your " \
                      "phone number, boots and motorcycle"
GREETING_AUTH = "Hey, <username>"

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
        request_confirmed = request_pending.to(authorized)

    def __init__(self, state='unauthorized'):
        self.state = state
        self.sm = self.AuthStateMachine(self)


auth = Authenticator(SAMPLE_DB)
auth_session_mock = AuthorizationSession()


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!",
        reply_markup=ReplyKeyboardMarkup.from_row(
            [KeyboardButton(text="Share phone number", request_contact=True)],
            one_time_keyboard=True))


def echo(update, context):
    if not auth_session_mock.sm.is_authorized:
        if auth_session_mock.sm.is_building_check:
            # TODO: check building
            auth_session_mock.sm.verify_building()
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="What is your appartment?")

        elif auth_session_mock.sm.is_apt_check:
            # TODO: check appartment
            auth_session_mock.sm.verify_appartment()
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="What is the name of the owner?")
        return

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=update.message.text)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Sorry, I didn't understand that command.")


def got_contact(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Checking for authorization",
                             reply_markup=ReplyKeyboardRemove())
    # TODO: actual check
    apt = auth.authenticate(update.message.contact.phone_number)
    if apt == auth.NO_PHONE_FOUND:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="User not found")
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="What is your building?")
        auth_session_mock.sm.init_registration()
    else:
        #TODO: main men
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Welcome to main menu!",
                                 reply_markup=InlineKeyboardMarkup.from_row(
                                     [InlineKeyboardButton(text="Show FAQ", callback_data="FAQ"),
                                      InlineKeyboardButton(text="My opened requests", callback_data="MyRequests"),
                                      InlineKeyboardButton(text="Create new request", callback_data="NewRequest")],
                                     one_time_keyboard=True))
        pass


def test_gdrive(update, context):
    # context.bot.send_message(chat_id=update.effective_chat.id,
    #                          text=src.gdrive.get_all())
    pass


def try_authorize(update, context):
    # TODO: Attach contact info
    is_authorized = db.is_authorized_contact()
    response = 'Welcome' if is_authorized else "You're not welcomed here"

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=response)
