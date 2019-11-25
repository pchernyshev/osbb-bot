from enum import unique, Enum, IntEnum
from functools import partial
from typing import List, Tuple, Dict, Iterable, Union

import gspread
from gspread import GSpreadException, Worksheet
from oauth2client.service_account import ServiceAccountCredentials

from config.config import GDRIVE_CRED, GDRIVE_URL
from src.db.base import AbstractDatabaseBridge, Address, ChatId, Phone, \
    TicketId, TicketData
from src.handler.const import TicketStatesStr


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
    Sheets.SERVICE: {
        Columns.SERVICE_POSSIBLE_STATUSES: 1
    }
}
_CURRENT_ID_CELL = (2, 2)


class SpreadsheetBridge(AbstractDatabaseBridge):
    """ Raises gspread.exceptions.GSpreadException in case of errors """

    TYPE_QUALIFIER = "google-spreadsheet"

    def __init__(self, config):
        super().__init__(config)

        # use creds to create a client to interact with the Google Drive API
        self.scope = ['https://spreadsheets.google.com/feeds']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(
            GDRIVE_CRED, self.scope)
        self.client = gspread.authorize(self.creds)

        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        self.doc = self.client.open_by_url(GDRIVE_URL)
        self.requests = self.doc.get_worksheet(Sheets.TICKETS.value)
        self.phone_db = self.doc.get_worksheet(Sheets.PHONES.value)
        self.pending = self.doc.get_worksheet(Sheets.REGISTRATIONS.value)
        self.faq = self.doc.get_worksheet(Sheets.FAQ.value)
        self.service = self.doc.get_worksheet(Sheets.SERVICE.value)

    def _address_checker(self, address: Address, r: Dict):
        return address == r[Columns.HOUSE.value], r[Columns.APT.value]

    def _ticket_checker(self, ticket_id: TicketId, r: Dict):
       return ticket_id == r[Columns.TICKET_ID.value]

    # TODO: Consider LUT?
    def __apt_data(self, work_sheet: Worksheet, address: Address)\
            ->Iterable[Dict]:
        yield from filter(partial(self._address_checker, address),
                          work_sheet.get_all_records())

    def __ticket(self, ticket_id: TicketId) -> Dict:
        return next(r
                    for r in self.requests.get_all_records()
                    if r[Columns.TICKET_ID.value] == ticket_id)

    def registered_phones(self, address: Union[None, Address])\
            -> Iterable[Tuple[ChatId, Phone, Address]]:
        filtered_source = self.__apt_data(self.phone_db, address)\
            if address else self.phone_db.get_all_records()

        yield from ((r[Columns.CHAT_ID.value], r[Columns.PHONE.value],
                     (r[Columns.HOUSE.value], r[Columns.APT.value]))
                    for r in filtered_source)

    def new_ticket(self, ticket: TicketData) -> TicketId:
        retries = 3
        current_id: int
        while retries:
            current_id = int(self.service.cell(*_CURRENT_ID_CELL).
                             numeric_value)
            self.service.update_cell(*_CURRENT_ID_CELL, current_id + 1)
            updated_id = int(self.service.cell(*_CURRENT_ID_CELL).
                             numeric_value)
            if updated_id == current_id + 1:
                break
            retries = retries - 1
        if not retries:
            raise RuntimeError("Race condition during update")

        self.requests.insert_row(
            [current_id,
             ticket.datetime.strftime("%d.%m.%y"),
             ticket.datetime.strftime("%H:%M"),
             ticket.chat_id,
             ticket.phone,
             ticket.address[0],
             ticket.address[1],
             ticket.category,
             ticket.description,
             ticket.media,
             TicketStatesStr.OPENED.value], index=2)

        return current_id

    def update_ticket(self, _id: TicketId, new_description, new_media):
        # TODO
        pass

    def tickets(self, address: Address) -> List[Tuple[TicketId, str]]:
        yield from self.__apt_data(self.requests, address)

    def get_ticket_details(self, ticket_id: TicketId):  # all ticket fields
        ticket = self.__ticket(ticket_id)
        from datetime import datetime
        return TicketData(
            chat_id=ticket[Columns.CHAT_ID.value],
            address=(ticket[Columns.HOUSE.value], ticket[Columns.APT.value]),
            phone=ticket[Columns.PHONE.value],
            datetime=datetime.strptime(ticket[Columns.TICKET_DATE.value]
                                       + " "
                                       + ticket[Columns.TICKET_TIME.value],
                                       "%d.%m.%y %H:%M"),
            category=ticket[Columns.TICKET_CATEGORY.value],
            description=ticket[Columns.TICKET_TEXT.value],
            media=ticket[Columns.TICKET_MEDIA.value]), ticket

    def new_registration(self, chat_id: ChatId, phone: Phone,
                         address: Address, comment: str):
        self.pending.insert_row(
            [chat_id, address[0], address[1], phone, comment], index=2)

    def peers(self, chat_id: ChatId, address: Address = None)\
            -> Iterable[ChatId]:
        """ Generates peer chat ids. Using address speed ups the process. """
        if not address:
            address = next(
                (r[Columns.HOUSE.value], r[Columns.APT.value])
                for r in self.pending.get_all_records()
                if r[Columns.CHAT_ID.value] == chat_id)

        yield from (r[Columns.CHAT_ID.value]
                    for r in self.__apt_data(self.phone_db, address))

    def peer_confirm(self, candidate_chat_id: ChatId):
        # TODO
        # Delete record in registrations
        # Insert record in phone_db
        pass

    def peer_reject(self, candidate_chat_id: ChatId):
        # TODO
        # Delete record in registrations
        pass

    def is_authorized(self, phone_or_chat_id: Union[Phone, ChatId]) -> bool:
        try:
            self.phone_db.find(str(phone_or_chat_id))
            return True
        except GSpreadException:
            return False

    def is_pending(self, phone_or_chat_id: Union[Phone, ChatId]) ->bool:
        try:
            self.pending.find(str(phone_or_chat_id))
            return True
        except GSpreadException:
            return False

    def update_registered_chat_id(self, phone: Phone, chat_id: ChatId):
        self.phone_db.update_cell(
            self.phone_db.find(phone).row,
            _SCHEMA[Sheets.REGISTRATIONS][Columns.CHAT_ID],
            chat_id)


