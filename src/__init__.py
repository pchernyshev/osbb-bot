from typing import List, Type

from src.db.base import AbstractDatabaseBridge
from src.db import *


REGISTERED_BRIDGES: List[Type[AbstractDatabaseBridge]] = \
    AbstractDatabaseBridge.__descendants__()
