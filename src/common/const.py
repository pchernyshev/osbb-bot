from enum import unique, Enum, auto
import gettext
_ = gettext.gettext

START_AUTHORIZED = False
CATEGORIES_IN_A_ROW = 3
DB_POLLING_INTERVAL = 10
REPORT_LOST_TICKETS = True
MAX_PHOTO_SIZE = 1024 ** 2  # MB


@unique
class AuthStates(Enum):
    UNAUTHORIZED_STATE = auto()
    PHONE_CHECKING_STATE = auto()
    HOUSE_CHECKING_STATE = auto()
    APARTMENT_CHECKING_STATE = auto()
    COMMEND_ADDING_STATE = auto()
    REQUEST_PENDING_STATE = auto()
    AUTHORIZED_STATE = auto()


@unique
class NewTicketStates(Enum):
    SELECTING_CATEGORY = auto()
    ENTERING_DESCRIPTION = auto()


@unique
class Flows(Enum):
    AUTHORIZATION = auto()
    MAIN_LOOP = auto()
    NEW_TICKET = auto()
    UPDATE_TICKETS = auto()


# TODO: map these to strings
@unique
class TicketsCategories(Enum):
    ELECTRICITY = "⚡ Електрика"
    WATER = "🛁 Вода"
    HEAT = "🌡️ Тепло"
    FACADE = "🧹 Чистота"
    SECURITY = "👮 Охорона"
    OTHER = "🛠️ Інше"


# TODO: map these to strings
@unique
class TicketStatesStr(Enum):
    OPENED = "Нова заявка"
    IN_PROGRESS = "В роботі"
    DONE = "Виконано"
    NEED_CLARIFICATION = "Потрібно уточнення"


# TODO: map these to strings
@unique
class InlineQueriesCb(Enum):
    TICKET_STOP = '✔ Завершити'
    TICKET_NEW = '📝 Нова заявка'
    TICKET_CANCEL = '❌ Відміна'
    AUTH_CHECK = 'AUTH_CHECK'
    AUTH_CONFIRM = 'AUTH_CONFIRM'
    AUTH_REJECT = 'AUTH_REJECT'
    MENU_FAQ = 'MENU_FAQ'
    MENU_MY_OPEN_TICKETS = 'MENU_MY_REQUESTS'
    MENU_NEW_TICKET = 'MENU_NEW_REQUEST'


# TODO: everything below needs to be merged with an actual code

SERVING_TO_NAME = _("SERVING_TO_NAME")
TICKET = _("TICKET")
TICKET_CATEGORY = _("TICKET_CATEGORY")
TICKET_DESCRIPTION = _("TICKET_DESCRIPTION")
TICKET_EXECUTION_COMMENTS = _("TICKET_EXECUTION_COMMENTS")
SELECT_TICKET_CATEGORY = _("SELECT_TICKET_CATEGORY")
CREATE_NEW_TICKET = _("CREATE_NEW_TICKET")
SHOW_MY_REQUESTS = _("SHOW_MY_REQUESTS")
FAQ_TITLE = _("FAQ_TITLE")
MENU_TITLE = _("MENU_TITLE")
NEED_PROPER_TICKET_COMMAND_FORMAT = _("NEED_PROPER_TICKET_COMMAND_FORMAT")
GREETING_FIRST_TIME1 = _("GREETING_FIRST_TIME1")
GREETING_FIRST_TIME2 = _("GREETING_FIRST_TIME2")
HI = _("HI")
AUTH_PENDING_FIRST_MESSAGE = _("AUTH_PENDING_FIRST_MESSAGE")
AUTH_IN_PROGRESS = _("AUTH_IN_PROGRESS")
AUTH_REJECTED = _("AUTH_REJECTED")
AUTHORIZED = _("AUTHORIZED")
CHECKING___ = _("CHECKING___")
WANTS_TO_REGISTER_AT_YOUR_APT = _("WANTS_TO_REGISTER_AT_YOUR_APT")
I_KNOW_THIS_PERSON = _("I_KNOW_THIS_PERSON")
I_DON_T_KNOW_THIS_PERSON = _("I_DON_T_KNOW_THIS_PERSON")
SHARE_PHONE_NUMBER = _("SHARE_PHONE_NUMBER")
NO_AUTH_BUT_I_KNOW_NUMBER = _("NO_AUTH_BUT_I_KNOW_NUMBER")
CANNOT_FIND_YOU = _("CANNOT_FIND_YOU")
WHERE_ARE_YOU_FROM = _("WHERE_ARE_YOU_FROM")
WHAT_APT_ARE_YOU_FROM = _("WHAT_APT_ARE_YOU_FROM")
AUTH_COMMENTS = _("AUTH_COMMENTS")
INVALID_PHONE_NUMBER = _("INVALID_PHONE_NUMBER")
INCORRECT_BUILDING = _("INCORRECT_BUILDING")
INCORRECT_APT = _("INCORRECT_APT")
LOOKING_FOR_YOU_IN_AUTH_DB = _("LOOKING_FOR_YOU_IN_AUTH_DB")
CHECK_STATUS = _("CHECK_STATUS")
I_HAVE_NO_TICKETS_OPENED_BY_YOU = _("I_HAVE_NO_TICKETS_OPENED_BY_YOU")
I_HAVE_CLOSED_TICKETS = _("I_HAVE_CLOSED_TICKETS")
PLEASE_DESCRIBE_A_PROBLEM = _("PLEASE_DESCRIBE_A_PROBLEM")
CANCEL_NEW_TICKET = _("CANCEL_NEW_TICKET")
TO_FINISH_USE = _("TO_FINISH_USE")
TO_CANCEL_USE = _("TO_CANCEL_USE")
TO_ADD_ANOTHER_ONE_USE = _("TO_ADD_ANOTHER_ONE_USE")
USE_A_COMMAND_TO_CHECK = _("USE_A_COMMAND_TO_CHECK")
I_OPENED_A_TICKET = _("I_OPENED_A_TICKET")
CANNOT_CREATE_TICKET_WITH_NO_DESCRIPTION =\
    _("CANNOT_CREATE_TICKET_WITH_NO_DESCRIPTION")
STARTED_PROGRESS = _("STARTED_PROGRESS")
TICKET_DONE = _("TICKET_DONE")
TICKET_LOST = _("TICKET_LOST")
UPLOADING_PHOTOS = _("UPLOADING_PHOTOS")
UPLOADED_PHOTOS = _("UPLOADED_PHOTOS")
CANNOT_SAVE_PHOTOS = _("CANNOT_SAVE_PHOTOS")
