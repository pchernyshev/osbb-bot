from abc import abstractmethod

from src.base import Discoverable


class AbstractDatabaseBridge(Discoverable):
    TYPE_QUALIFIER = '^$'  # not respond to discovery

    @abstractmethod
    def _get_registered_phones(self): pass

    @abstractmethod
    def is_authorized_contact(self):
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
