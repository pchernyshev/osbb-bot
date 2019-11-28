from src import AbstractDatabaseBridge
from src.handler.const import AuthStates, START_AUTHORIZED


class Client:
    def __init__(self, phone="", house="", apt=0,
                 authorized: bool = START_AUTHORIZED):
        self.auth_state = AuthStates.AUTHORIZED_STATE\
            if START_AUTHORIZED else AuthStates.UNAUTHORIZED_STATE
        self.phone = ""
        self.house = ""
        self.apt = 0

    @classmethod
    def from_context(cls, context):
        client = context.user_data.get('client')
        if not client:
            client = cls()
            context.user_data['client'] = client

        return client

    @classmethod
    def from_db(cls, chat_id, db: AbstractDatabaseBridge):
        # TODO: typing for record
        for record in db.registered_phones(None):
            if record[0] == chat_id:
                return cls(authorized=True, phone=record[1],
                           house=record[2][0], apt=record[2][1])
        else:
            return None

    def is_valid(self):
        return self.phone and self.house and self.apt\
               and self.auth_state == AuthStates.AUTHORIZED_STATE

