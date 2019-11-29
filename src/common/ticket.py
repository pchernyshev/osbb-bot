from collections import namedtuple
from typing import Tuple, Dict

from statemachine import StateMachine, State

from src.common.const import TICKET, TICKET_CATEGORY, TICKET_DESCRIPTION, \
    TICKET_EXECUTION_COMMENTS
from src.common.tg_utils import ticket_link

TicketData = namedtuple("TicketData",
                        "chat_id, phone, address, datetime, category, "
                        "description, media")


def ticket_status(ticket_raw: Tuple[TicketData, Dict]) -> str:
    return ticket_raw[1]['status']


def ticket_id(ticket_raw: Tuple[TicketData, Dict]) -> str:
    return ticket_raw[1]['id']


def ticket_formatter(ticket: Tuple[TicketData, Dict]) -> str:
    s = f"{TICKET} {ticket_link(ticket[1]['id'])} " \
        f"({ticket[1]['date_text']} {ticket[1]['time_text']}): " \
        f"{ticket_status(ticket)}\n" \
        f"{TICKET_CATEGORY}: {ticket[0].category}\n" \
        f"{TICKET_DESCRIPTION}: {ticket[0].description}\n"

    if ticket[1]['comments']:
        s += f"{TICKET_EXECUTION_COMMENTS}: {ticket[1]['comments']}"

    return s


class TicketMachine(StateMachine):
    opened = State('Открытая заявка', initial=True)
    in_progress = State('В процессе')
    need_clarification = State('Уточняется')
    declined = State('Отклонена')
    done = State('Выполнена')
    need_verification = State('Проверяется')

    clarify = opened.to(need_clarification)
    clarified = need_clarification.to(in_progress)
    cancel = need_clarification.to(declined) | opened.to(declined)
    verify = in_progress.to(need_verification)
    close = need_verification.to(done)
    start_progress = opened.to(in_progress)

# t.actions.clarify()
# print(f"States: {t.state}/{t2.state}")
# t.actions.clarified()
# print(f"States: {t.state}/{t2.state}")
# t2.actions.clarify()
# print(f"States: {t.state}/{t2.state}")
# t2.actions.decline_after_clarification()
# print(f"States: {t.state}/{t2.state}")
# t.actions.verify()
# print(f"States: {t.state}/{t2.state}")
# t.actions.close()
# print(f"States: {t.state}/{t2.state}")
