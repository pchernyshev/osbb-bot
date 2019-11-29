import json
from datetime import datetime
from functools import partial
from threading import RLock
from typing import List, Tuple, Dict, Iterable, Union

from gspread import GSpreadException, Worksheet, Client

from config.config import GDRIVE_CRED, GDRIVE_URL
from src.common.const import TicketStatesStr
from src.common.ticket import TicketData
from src.db.base import AbstractDatabaseBridge, Address, ChatId, Phone, \
    TicketId
from src.db.google_ss_schema import Columns, Sheets, _SCHEMA, _CURRENT_ID_CELL


class SpreadsheetBridge(AbstractDatabaseBridge):
    """ Raises gspread.exceptions.GSpreadException in case of errors """

    TYPE_QUALIFIER = "google-spreadsheet"
    MAX_NUMBER_RETRIES_TABLE_UPDATE = 3

    @staticmethod
    def __create_assertion_session(conf_file, scopes, subject=None):
        with open(conf_file, 'r') as f:
            conf = json.load(f)

        token_url = conf['token_uri']
        issuer = conf['client_email']
        key = conf['private_key']
        key_id = conf.get('private_key_id')

        header = {'alg': 'RS256'}
        if key_id:
            header['kid'] = key_id

        # Google puts scope in payload
        claims = {'scope': ' '.join(scopes)}
        from authlib.integrations.requests_client import AssertionSession
        return AssertionSession(
            grant_type=AssertionSession.JWT_BEARER_GRANT_TYPE,
            token_url=token_url,
            issuer=issuer,
            audience=token_url,
            claims=claims,
            subject=subject,
            key=key,
            header=header,
            token_endpoint=True
        )

    def __init__(self, config):
        super().__init__(config)

        # use creds to create a client to interact with the Google Drive API
        self.scope = ['https://spreadsheets.google.com/feeds',
                      'https://www.googleapis.com/auth/drive']
        self.session = self.__create_assertion_session(GDRIVE_CRED, self.scope)
        self.client = Client(None, self.session)

        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        self.doc = self.client.open_by_url(GDRIVE_URL)
        self.requests = self.doc.get_worksheet(Sheets.TICKETS.value)
        self.phone_db = self.doc.get_worksheet(Sheets.PHONES.value)
        self.pending = self.doc.get_worksheet(Sheets.REGISTRATIONS.value)
        self.faq = self.doc.get_worksheet(Sheets.FAQ.value)
        self.service = self.doc.get_worksheet(Sheets.SERVICE.value)
        self.table_lock = RLock()

    @staticmethod
    def _address_checker(address: Address, r: Dict):
        return address == (r[Columns.HOUSE.value], r[Columns.APT.value])

    @staticmethod
    def _ticket_checker(ticket_id: TicketId, r: Dict):
        return ticket_id == r[Columns.TICKET_ID.value]

    def _apt_data(self, work_sheet: Worksheet, address: Address)\
            ->Iterable[Dict]:
        yield from filter(partial(self._address_checker, address),
                          work_sheet.get_all_records())

    def __ticket(self, ticket_id: TicketId) -> Dict:
        return next(r for r in self.requests.get_all_records()
                    if r[Columns.TICKET_ID.value] == ticket_id)

    def registered_phones(self, address: Union[None, Address])\
            -> Iterable[Tuple[ChatId, Phone, Address]]:
        filtered_source = self._apt_data(self.phone_db, address)\
            if address else self.phone_db.get_all_records()

        yield from ((r[Columns.CHAT_ID.value], r[Columns.PHONE.value],
                     (r[Columns.HOUSE.value], r[Columns.APT.value]))
                    for r in filtered_source)

    def new_ticket(self, ticket: TicketData) -> TicketId:
        retries = self.MAX_NUMBER_RETRIES_TABLE_UPDATE
        current_id: int
        with self.table_lock:
            while retries:
                current_id = int(self.service.cell(*_CURRENT_ID_CELL).
                                 numeric_value)
                self.service.update_cell(*_CURRENT_ID_CELL, current_id + 1)
                updated_id = int(self.service.cell(*_CURRENT_ID_CELL).
                                 numeric_value)
                if updated_id == current_id + 1:
                    break
                retries = retries - 1
            else:
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
        with self.table_lock:
            # TODO: add update ticket routine
            pass

    @staticmethod
    def __record_to_ticket(record: Dict) -> Tuple[TicketData, Dict]:
        return TicketData(
            chat_id=record[Columns.CHAT_ID.value],
            address=(record[Columns.HOUSE.value], record[Columns.APT.value]),
            phone=record[Columns.PHONE.value],
            datetime=datetime.strptime(record[Columns.TICKET_DATE.value]
                                       + " "
                                       + record[Columns.TICKET_TIME.value],
                                       "%d.%m.%y %H:%M"),
            category=record[Columns.TICKET_CATEGORY.value],
            description=record[Columns.TICKET_TEXT.value],
            media=record[Columns.TICKET_MEDIA.value]), {
                   'id': record[Columns.TICKET_ID.value],
                   'status': record[Columns.TICKET_STATUS.value],
                   'comments': record[Columns.TICKET_PUBLIC_COMMENTS.value],
                   'private': record[Columns.TICKET_PRIVATE_COMMENTS.value],
                   'date_text': record[Columns.TICKET_DATE.value],
                   'time_text': record[Columns.TICKET_TIME.value],
               }

    def tickets(self, address: Address) -> List[Tuple[TicketData, Dict]]:
        yield from (self.__record_to_ticket(r)
                    for r in self._apt_data(self.requests, address))

    def get_ticket_details(self, ticket_id: TicketId):  # all ticket fields
        return self.__record_to_ticket(self.__ticket(ticket_id))

    def new_registration(self, chat_id: ChatId, phone: Phone,
                         address: Address, comment: str):
        self.pending.insert_row(
            [chat_id, address[0], address[1], phone, comment], index=2)

    def peers(self, chat_id: ChatId, address: Address = None)\
            -> Iterable[ChatId]:
        """
        Generates peer chat ids by address.
        Using address speed ups the process.
        chat_id is used only if address is not supplied
        """
        if not address:
            address = next(
                (r[Columns.HOUSE.value], r[Columns.APT.value])
                for r in self.pending.get_all_records()
                if r[Columns.CHAT_ID.value] == chat_id)

        yield from (r[Columns.CHAT_ID.value]
                    for r in self._apt_data(self.phone_db, address))

    def peer_confirm(self, phone_or_chat_id: Union[Phone, ChatId]):
        from operator import itemgetter
        with self.table_lock:
            registration = dict(zip([k for k, _ in sorted(
                _SCHEMA[Sheets.REGISTRATIONS].items(), key=itemgetter(1))],
                                    self.peer_reject(phone_or_chat_id)))
            self.phone_db.insert_row(
                [registration[k]
                 for k, _ in sorted(_SCHEMA[Sheets.PHONES].items(),
                                    key=itemgetter(1))],
                index=2)

    def peer_reject(self, phone_or_chat_id: Union[Phone, ChatId]):
        with self.table_lock:
            reg_found = self.pending.find(str(phone_or_chat_id))
            reg_cells = self.pending.row_values(reg_found.row)
            self.pending.delete_row(reg_found.row)
            return reg_cells

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
        with self.table_lock:
            self.phone_db.update_cell(
                self.phone_db.find(str(phone)).row,
                _SCHEMA[Sheets.REGISTRATIONS][Columns.CHAT_ID],
                chat_id)

    def snapshot_ticket_statuses(self) -> Dict[TicketId, Tuple[Address, str]]:
        return {r[Columns.TICKET_ID.value]:
                ((r[Columns.HOUSE.value], r[Columns.APT.value]),
                    r[Columns.TICKET_STATUS.value])
                for r in self.requests.get_all_records()}

    def fetch_faq(self) -> Iterable[Tuple[str, str]]:
        yield from ((r[Columns.FAQ_Q.value], r[Columns.FAQ_A.value])
                    for r in self.faq.get_all_records())
