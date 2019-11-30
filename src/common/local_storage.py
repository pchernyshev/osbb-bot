from typing import Dict

from src import AbstractDatabaseBridge
from src.common.const import AuthStates, START_AUTHORIZED


class Client:
    def __init__(self, phone="", house="", apt=0,
                 authorized: bool = START_AUTHORIZED):
        self.auth_state = AuthStates.AUTHORIZED_STATE \
            if authorized else AuthStates.UNAUTHORIZED_STATE
        self.phone = phone
        self.house = house
        self.apt = apt

    @classmethod
    def from_context(cls, context):
        client = context.user_data.get('client')
        if not client:
            client = cls()
            context.user_data['client'] = client

        return client

    def update_from_db(self, chat_id, db: AbstractDatabaseBridge):
        # TODO: typing for record
        for record in db.registered_phones(None):
            if record[0] == chat_id:
                self.auth_state = AuthStates.AUTHORIZED_STATE
                self.phone = record[1]
                self.house = record[2][0]
                self.apt = record[2][1]

    def is_valid(self):
        return self.phone and self.house and self.apt\
               and self.auth_state == AuthStates.AUTHORIZED_STATE


def ticket_from_context(context, new_ticket = False) -> Dict:
    ticket = context.chat_data.get('current_ticket')
    if not ticket or new_ticket:
        ticket = {
            'category': "",
            'messages': [],
            'media': [],
            'media_dir': ""
        }
        context.chat_data['current_ticket'] = ticket

    return ticket
