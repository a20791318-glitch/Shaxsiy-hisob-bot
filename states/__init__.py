from aiogram.fsm.state import State, StatesGroup


class IncomeState(StatesGroup):
    cash_amount = State()
    card_amount = State()
    currency_amount = State()


class ExpenseState(StatesGroup):
    add_category = State()
    expense_amount = State()


class DebtTakeState(StatesGroup):
    person = State()
    amount = State()
    comment = State()


class DebtGiveState(StatesGroup):
    person = State()
    amount = State()
    comment = State()


class DebtPayState(StatesGroup):
    amount = State()


class DebtReturnState(StatesGroup):
    amount = State()


class SupportState(StatesGroup):
    message = State()


class SupportReplyState(StatesGroup):
    message = State()


class BroadcastState(StatesGroup):
    message = State()


class RestoreState(StatesGroup):
    file = State()
