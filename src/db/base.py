from abc import abstractmethod
from typing import Tuple, List

from src.base import Discoverable

Address = Tuple[str, str]
Phone = str
TicketId = str
ChatId = str


class AbstractDatabaseBridge(Discoverable):
    TYPE_QUALIFIER = '^$'  # not respond to discovery

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def _get_registered_phones(self, address: Address)\
            -> List[Tuple[ChatId, Phone]]:
        pass

    @abstractmethod
    def new_ticket(self, category, description, address: Address, media)\
            -> TicketId:
        pass

    @abstractmethod
    def update_ticket(self, _id: TicketId, new_description, new_media):
        pass

    @abstractmethod
    def get_tickets(self, address: Address) -> List[Tuple[TicketId, str]]:
        pass

    @abstractmethod
    def get_ticket_details(self, ticket: TicketId):  # all ticket fields
        pass

    @abstractmethod
    def new_registration(self, chat_id: ChatId, phone: Phone,
                         address: Address, owner_contact: str) -> bool:
        pass

    @abstractmethod
    def peer_confirm(self, candidate_chat_id: ChatId):
        pass

    @abstractmethod
    def peer_reject(self, candidate_chat_id: ChatId):
        pass

    @abstractmethod
    def is_authorized_contact(self, phone: Phone) -> bool:
        # TODO: update signature
        pass



# TODO: future SQL-alike connection
# import pyodbc
# from typing import Dict, Union, TextIO
# class DatabaseContext:
#     def __init__(self, config: Union[Dict[str, str], str, TextIO]):
#         self._cnxn: pyodbc.Connection = None
#         if isinstance(config, str):
#             conn_str = config
#         elif isinstance(config, dict):
#             conn_str = self._conn_from_dict(config)
#         else:
#             raise ValueError(f"Wrong configuration: {config}")
#
#         self._cnxn = pyodbc.connect(conn_str)
#
#     @staticmethod
#     def _conn_from_dict(conf: dict) -> str:
#         return ';'.join([f'{k}={v}' for k, v in conf.items()])
#
#     @property
#     def connection(self) -> pyodbc.Connection:
#         return self._cnxn

# # connection string
# db = DatabaseContext("Driver=SQLite3;Database=sqlite.db")
# conn = db.connection
# conn.execute("SELECT * FROM table")

# # connection config
# conf = dict(Driver="SQLite3", Databse="sqlite.db")
# db = DatabaseContext(conf)
# conn = db.connection
# conn.execute("SELECT * FROM table")
