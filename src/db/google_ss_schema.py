from enum import unique, Enum, IntEnum


@unique
class Columns(Enum):
    CHAT_ID = 'chat_id'
    HOUSE = 'Будинок'
    APT = 'Квартира'
    PHONE = 'Телефон'
    TICKET_ID = 'Номер'
    TICKET_DATE = 'Дата'
    TICKET_TIME = 'Час'
    TICKET_CATEGORY = 'Категорія'
    TICKET_TEXT = 'Текст заявки'
    TICKET_MEDIA = 'Фото'
    TICKET_STATUS = 'Статус'
    TICKET_PUBLIC_COMMENTS = 'Коментарі'
    TICKET_PRIVATE_COMMENTS = 'Приватні коментарі'
    REGISTRATION_COMMENT = 'Коментар'
    SERVICE_POSSIBLE_STATUSES = 'Статусы заявок'
    FAQ_Q = 'Питання'
    FAQ_A = 'Відповідь'


@unique
class Sheets(IntEnum):
    TICKETS = 0
    PHONES = 1
    REGISTRATIONS = 2
    FAQ = 3
    SERVICE = 4


_SCHEMA = {
    Sheets.TICKETS: {
        # Hidden: 1
        Columns.TICKET_ID: 2,
        Columns.TICKET_DATE: 3,
        Columns.TICKET_TIME: 4,
        Columns.CHAT_ID: 5,
        Columns.PHONE: 6,
        Columns.HOUSE: 7,
        Columns.APT: 8,
        Columns.TICKET_CATEGORY: 9,
        Columns.TICKET_TEXT: 10,
        Columns.TICKET_MEDIA: 11,
        Columns.TICKET_STATUS: 12,
        Columns.TICKET_PUBLIC_COMMENTS: 13,
        Columns.TICKET_PRIVATE_COMMENTS: 14
    },
    Sheets.PHONES: {
        Columns.CHAT_ID: 1,
        Columns.HOUSE: 2,
        Columns.APT: 3,
        Columns.PHONE: 4
    },
    Sheets.REGISTRATIONS: {
        Columns.CHAT_ID: 1,
        Columns.HOUSE: 2,
        Columns.APT: 3,
        Columns.PHONE: 4,
        Columns.REGISTRATION_COMMENT: 5
    },
    Sheets.FAQ: {
        Columns.FAQ_Q: 1,
        Columns.FAQ_A: 2
    },
    Sheets.SERVICE: {
        Columns.SERVICE_POSSIBLE_STATUSES: 1
    }
}
_CURRENT_ID_CELL = (2, 2)