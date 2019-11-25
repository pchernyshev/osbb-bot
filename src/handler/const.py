from enum import unique, Enum, auto


START_AUTHORIZED = False


@unique
class AuthStates(Enum):
    UNAUTHORIZED_STATE = auto()
    PHONE_CHEKING_STATE = auto()
    HOUSE_CHECKING_STATE = auto()
    APARTMENT_CHECKING_STATE = auto()
    OWNER_FILLING_STATE = auto()
    REQUEST_PENDING_STATE = auto()
    AUTHORIZED_STATE = auto()


@unique
class NewTicketStates(Enum):
    SELECTING_CATEGORY = auto()
    ENTERING_DESCRIPTION = auto()
    ATTACHING_PHOTOS = auto()
    REVIEW = auto()
    OPENING_NEW_TICKET = auto()


@unique
class Flows(Enum):
    AUTHORIZATION = auto()
    MAIN_LOOP = auto()
    NEW_TICKET = auto()
    LIST_TICKETS = auto()
    FAQ = auto()
    UPDATE_TICKETS = auto()


@unique
class TicketsCategories(Enum):
    ELECTRICITY = "Electricity"
    WATER = "Water"
    HEAT = "Heating"
    FACADE = "Facade/cleaning"  # and cleaning
    SECURITY = "Security"
    OTHER = "Other"

@unique
class TicketStatesStr(Enum):
    OPENED = "Нова заявка"
    IN_PROGRESS = "В роботі"
    DONE = "Виконано"
    NEED_CLARIFICATION = "Потрібно уточнення"
