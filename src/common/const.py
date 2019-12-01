from enum import unique, Enum, auto

START_AUTHORIZED = False
CATEGORIES_IN_A_ROW = 3
DB_POLLING_INTERVAL = 10
REPORT_LOST_TICKETS = True
MAX_PHOTO_SIZE = 1024 ** 2  # MB


@unique
class AuthStates(Enum):
    UNAUTHORIZED_STATE = auto()
    PHONE_CHECKING_STATE = auto()
    HOUSE_CHECKING_STATE = auto()
    APARTMENT_CHECKING_STATE = auto()
    COMMEND_ADDING_STATE = auto()
    REQUEST_PENDING_STATE = auto()
    AUTHORIZED_STATE = auto()


@unique
class NewTicketStates(Enum):
    SELECTING_CATEGORY = auto()
    ENTERING_DESCRIPTION = auto()


@unique
class Flows(Enum):
    AUTHORIZATION = auto()
    MAIN_LOOP = auto()
    NEW_TICKET = auto()
    UPDATE_TICKETS = auto()


@unique
class TicketsCategories(Enum):
    ELECTRICITY = "⚡ Електрика"
    WATER = "🛁 Вода"
    HEAT = "🌡️ Тепло"
    FACADE = "🧹 Чистота"  # and cleaning
    SECURITY = "👮 Охорона"
    OTHER = "🛠️ Інше"


@unique
class TicketStatesStr(Enum):
    OPENED = "Нова заявка"
    IN_PROGRESS = "В роботі"
    DONE = "Виконано"
    NEED_CLARIFICATION = "Потрібно уточнення"


@unique
class InlineQueriesCb(Enum):
    TICKET_STOP = '✔ Завершити'
    TICKET_CANCEL = '❌ Відміна'
    AUTH_CHECK = 'AUTH_CHECK'
    AUTH_CONFIRM = 'AUTH_CONFIRM'
    AUTH_REJECT = 'AUTH_REJECT'
    MENU_FAQ = 'MENU_FAQ'
    MENU_MY_OPEN_TICKETS = 'MENU_MY_REQUESTS'
    MENU_NEW_TICKET = 'MENU_NEW_REQUEST'


SERVING_TO_NAME = "ОСББ"

TICKET = "Заявка"
TICKET_CATEGORY = "Категорія"
TICKET_DESCRIPTION = "Опис"
TICKET_EXECUTION_COMMENTS = "Коментарі виконавця"

SELECT_TICKET_CATEGORY = "Оберіть категорію заявки"
CREATE_NEW_TICKET = "Створити нову заявку"
SHOW_MY_REQUESTS = "Мої відкриті заявки"
FAQ_TITLE = "Часті питання"
MENU_TITLE = "Що ви бажаєте зробити?"
NEED_PROPER_TICKET_COMMAND_FORMAT = "Мені потрібен номер заявки цифрами."


GREETING_FIRST_TIME = f"Привіт! Я бот на службі {SERVING_TO_NAME}. " \
    "Щоб обслуговувати вас мені потрібен ваш контактний номер."
HI = "Привіт"
AUTH_PENDING_FIRST_MESSAGE = "Я запитав, чи можу вас обслуговувати"
AUTH_IN_PROGRESS = \
    "В мене є запис про реєстрацію. Адміністратор повинен його одобрити."
AUTH_REJECTED = \
    "Дуже щкода, але здається вашу реєстрацію відмінено.\n" \
    "Ви можете заповнити заявку знова, використовуючи команду /start"
AUTHORIZED = "Вас авторизовано"
CHECKING___ = "Перевіряю..."
WANTS_TO_REGISTER_AT_YOUR_APT = "хоче зареєструватися за вашою адресою"
I_KNOW_THIS_PERSON = "Все добре, я знаю, хто це."
I_DON_T_KNOW_THIS_PERSON = "Я не знаю цей номер."
SHARE_PHONE_NUMBER = "Поділитися номером телефону"
NO_AUTH_BUT_I_KNOW_NUMBER = "Я про вас десь чув. Добрий день!"
CANNOT_FIND_YOU = "Я не можу знайти вас у базі."
WHERE_ARE_YOU_FROM = "З якого ви будинку?"
WHAT_APT_ARE_YOU_FROM = "З якої ви квартири?"
AUTH_COMMENTS = \
    "Добре. Додайте якийсь коментар, що допоможе адміністратору вас " \
    "впізнати (так, він лише людина). Наприклад, хто володіє цією квартирою?"
INVALID_PHONE_NUMBER = \
    "Вибачте, але це не дуже схоже на правильний номер телефона."
INCORRECT_BUILDING = "Вибачте, але це схоже неправильний номер дома."
INCORRECT_APT = "Я не впевнен, що це існуючий номер квартири."
LOOKING_FOR_YOU_IN_AUTH_DB = "Шукаю ваш контакт у базі..."
CHECK_STATUS = "Перевірити статус реєстрації"


I_HAVE_NO_TICKETS_OPENED_BY_YOU = "В вас, схоже, немає відкритих заявок."
I_HAVE_CLOSED_TICKETS = "В вас також є закриті заявки"
PLEASE_DESCRIBE_A_PROBLEM = "Будь-ласка, опишіть проблему. "
ADD_MORE_DESCRIPTION = "Ви можете додати ще опису чи фотогрфій."
CANCEL_NEW_TICKET = "Відміна створення заявки"
TO_FINISH_USE = "Щоб закінчити додавати заявку, оберіть "
TO_CANCEL_USE = "Щоб відмінити створення заявки: "

USE_A_COMMAND_TO_CHECK = "Щоб перевірити статус введіть, чи натисніть: "

I_OPENED_A_TICKET = "Я зареєстрував нову заявку. "
CANNOT_CREATE_TICKET_WITH_NO_DESCRIPTION =\
    "Я не можу відкрити заявку без тексту."

STARTED_PROGRESS = "Заявка виконується"
TICKET_DONE = "Заявка опрацьована"
TICKET_LOST = "Статус заявки втрачен, будь ласка зверніться до управління"

UPLOADING_SINGLE_PHOTO = "Зберігаю фотографію. "
UPLOADING_PHOTOS = "Зберігаю фотографії в заявку..."
UPLOADED_PHOTOS = "Все добре, фотографії додано."
CANNOT_SAVE_PHOTOS = "Я не збіг зберегти фотографії :("
