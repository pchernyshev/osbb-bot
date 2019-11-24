from typing import List, Tuple

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from src.db.base import AbstractDatabaseBridge, Address, ChatId, Phone, \
    TicketId
from src.sheet_markup import RequestsSheet, Request


class SpreadsheetBridge(AbstractDatabaseBridge):
    TYPE_QUALIFIER = "google-spreadsheet"

    def __init__(self, config):
        super().__init__(config)

        # use creds to create a client to interact with the Google Drive API
        self.scope = ['https://spreadsheets.google.com/feeds']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(
            config.GDRIVE_CRED, self.scope)
        self.client = gspread.authorize(self.creds)

        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        # sheet = client.open("OSBBotSheet").sheet1
        self.doc = self.client.open_by_url(config.GDRIVE_URL)
        self.requests = RequestsSheet(self.doc)

    def test_get_request(self):
        row = 2
        return self.requests.get(Request.USER_NAME, row) \
               + " (" + self.requests.get(Request.PHONE, row) + ")"
        # return RequestFields.USER_NAME.get(doc, row) + " (" + RequestFields.PHONE.get(doc, row) + ")"

    # Extract and print all of the values
    # def test_get_all():
    #     return self.doc.sheet1.get_all_values()

    # TODO: integrate with spreadsheets
    def _get_registered_phones(self, address: Address)\
            -> List[Tuple[ChatId, Phone]]:
        pass

    def new_ticket(self, category, description, address: Address, media)\
            -> TicketId:
        pass

    def update_ticket(self, _id: TicketId, new_description, new_media):
        pass

    def get_tickets(self, address: Address) -> List[Tuple[TicketId, str]]:
        pass

    def get_ticket_details(self, ticket: TicketId):  # all ticket fields
        pass

    def new_registration(self, chat_id: ChatId, phone: Phone,
                         address: Address, owner_contact: str) -> bool:
        pass

    def peer_confirm(self, candidate_chat_id: ChatId):
        pass

    def peer_reject(self, candidate_chat_id: ChatId):
        pass

    def is_authorized_contact(self, phone: Phone) -> bool:
        # TODO: update signature
        pass

