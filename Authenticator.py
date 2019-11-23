from enum import Enum
from typing import Dict, List

__SAMPLE_DB = {
    1: ["+380501234567"],
    2: ["+15559876543", "+15551234567"]
}


class Authenticator:
    NO_PHONE_FOUND = -1

    def __init__(self, db: Dict[int, List[str]] = None):
        self.db = dict(db)

    def authenticate(self, phone: str):
        """
        >>> Authenticator(db=__SAMPLE_DB).authenticate(__SAMPLE_DB[1][0])
        1
        >>> Authenticator(db=__SAMPLE_DB).authenticate(__SAMPLE_DB[2][0])
        2
        >>> Authenticator(db=__SAMPLE_DB).authenticate(__SAMPLE_DB[2][1])
        2
        >>> Authenticator(db=__SAMPLE_DB).authenticate("gibberish")
        -1

        :param apt: a number of appartments, should be unique in DB
        :param phone: a string containing properly formatted phone number
        :return:
        """
        apt = [k for k, v in self.db.items() if phone in v]
        if not apt:
            return self.NO_PHONE_FOUND
        else:
            return apt[0]

    def fetch_db(self):
        pass

    def dump_db(self):
        pass


if __name__ == "__main__":
    import doctest
    doctest.testmod()
