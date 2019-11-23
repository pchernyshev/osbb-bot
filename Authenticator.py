from enum import Enum
from typing import Dict, List

__SAMPLE_DB = {
    1: ["+380501234567"],
    2: ["+15559876543", "+15551234567"]
}


class AuthStatus(Enum):
    NO_APT = 1
    NO_PHONE = 2
    OK = 3


class Authenticator:
    def __init__(self, db: Dict[int, List[str]] = None):
        self.db = dict(db)

    def authenticate(self, apt: int, phone: str):
        """
        >>> Authenticator(db=__SAMPLE_DB).authenticate(1, __SAMPLE_DB[1][0])
        <AuthStatus.OK: 3>
        >>> Authenticator(db=__SAMPLE_DB).authenticate(2, __SAMPLE_DB[2][0])
        <AuthStatus.OK: 3>
        >>> Authenticator(db=__SAMPLE_DB).authenticate(2, __SAMPLE_DB[2][1])
        <AuthStatus.OK: 3>
        >>> Authenticator(db=__SAMPLE_DB).authenticate(3, __SAMPLE_DB[2][1])
        <AuthStatus.NO_APT: 1>
        >>> Authenticator(db=__SAMPLE_DB).authenticate(1, "gibberish")
        <AuthStatus.NO_PHONE: 2>
        >>> Authenticator(db=__SAMPLE_DB).authenticate("gibberish", "gibberish")
        <AuthStatus.NO_APT: 1>
        >>> Authenticator(db=__SAMPLE_DB).authenticate(None, "gibberish")
        <AuthStatus.NO_APT: 1>

        :param apt: a number of appartments, should be unique in DB
        :param phone: a string containing properly formatted phone number
        :return:
        """
        record = self.db.get(apt)
        if record is None:
            return AuthStatus.NO_APT
        elif phone not in record:
            return AuthStatus.NO_PHONE
        else:
            return AuthStatus.OK

    def fetch_db(self):
        pass

    def dump_db(self):
        pass


if __name__ == "__main__":
    import doctest
    doctest.testmod()
