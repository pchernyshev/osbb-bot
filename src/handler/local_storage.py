from src import AbstractDatabaseBridge
from src.handler.const import AuthStates, START_AUTHORIZED


class Client:
    def __init__(self):
        self.auth_state = AuthStates.AUTHORIZED_STATE\
            if START_AUTHORIZED else AuthStates.UNAUTHORIZED_STATE
        self.phone = ""
        self.house = ""
        self.apt = 0

    @staticmethod
    def get_client_from_context(context):
        client = context.user_data.get('client')
        if not client:
            client = Client()
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

