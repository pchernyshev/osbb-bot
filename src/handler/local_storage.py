from collections import defaultdict

from src.handler.const import AuthStates, START_AUTHORIZED


class Client:
    def __init__(self, locale='uk'):
        self.auth_state = AuthStates.AUTHORIZED_STATE\
            if START_AUTHORIZED else AuthStates.UNAUTHORIZED_STATE
        self.locale = locale
        self.phone = ""
        self.building = ""
        self.apt = 0
        self.owner = ""
        self.update_locale(locale)

    def update_locale(self, locale):
        #self.locale = Locale.parse(locale)
        pass


LOCAL_STORAGE = defaultdict(Client)
