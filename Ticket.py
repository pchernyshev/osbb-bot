from statemachine import StateMachine, State


class TicketMachine(StateMachine):
    opened = State('Открытая заявка', initial=True)
    in_progress = State('В процессе')
    need_clarification = State('Уточняется')
    declined = State('Отклонена')
    done = State('Выполнена')
    need_verification = State('Проверяется')

    clarify = opened.to(need_clarification)
    clarified = need_clarification.to(in_progress)
    decline_after_clarification = need_clarification.to(declined)
    cancel_opened = opened.to(declined)
    verify = in_progress.to(need_verification)
    close = need_verification.to(done)
    start_progress = opened.to(in_progress)


class Ticket:
    def __init__(self, state='opened'):
        self.state = state
        self.actions = TicketMachine(self)


# t = Ticket()
# t2 = Ticket()
#
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

