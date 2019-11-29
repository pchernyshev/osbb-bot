from abc import abstractmethod
from typing import Tuple, Iterable, Dict, Union

from src.common.base import Discoverable
from src.common.ticket import TicketData

Address = Tuple[str, int]
Phone = str
TicketId = int
ChatId = str


class AbstractDatabaseBridge(Discoverable):
    TYPE_QUALIFIER = '^$'  # not respond to discovery

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def registered_phones(self, address: Union[None, Address])\
        -> Iterable[Tuple[ChatId, Phone]]: pass

    @abstractmethod
    def new_ticket(self, ticket: TicketData) -> TicketId: pass

    @abstractmethod
    def update_ticket(self, _id: TicketId, new_description, new_media): pass

    @abstractmethod
    def tickets(self, address: Address)\
        -> Iterable[Tuple[TicketData, Dict]]: pass

    @abstractmethod
    def get_ticket_details(self, ticket: TicketId)\
        -> Tuple[TicketData, Dict]: pass

    @abstractmethod
    def new_registration(self, chat_id: ChatId, phone: Phone,
                         address: Address, owner_contact: str) -> bool: pass

    @abstractmethod
    def peers(self, chat_id: ChatId, address: Address = None)\
        -> Iterable[ChatId]: pass

    @abstractmethod
    def peer_confirm(self, phone_or_chat_id: Union[Phone, ChatId]): pass

    @abstractmethod
    def peer_reject(self, phone_or_chat_id: Union[Phone, ChatId]): pass

    @abstractmethod
    def is_authorized(self, phone_or_chat_id: Union[Phone, ChatId]) -> bool:
        pass

    @abstractmethod
    def update_registered_chat_id(self, phone: Phone, chat_id: ChatId): pass

    @abstractmethod
    def is_pending(self, phone_or_chat_id) -> bool: pass

    @abstractmethod
    def snapshot_ticket_statuses(self) \
        -> Dict[TicketId, Tuple[Address, str]]: pass

    @abstractmethod
    def fetch_faq(self) -> Iterable[Tuple[str, str]]: pass


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
# conf = dict(Driver="SQLite3", Database="sqlite.db")
# db = DatabaseContext(conf)
# conn = db.connection
# conn.execute("SELECT * FROM table")
