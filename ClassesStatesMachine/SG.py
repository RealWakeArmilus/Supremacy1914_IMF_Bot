# import StatesGroup
from aiogram.fsm.state import StatesGroup, State


# Определите состояния для хранения message_id
class SavePhotoMessageID(StatesGroup):
    photo_message_id = State()


class FormCreatedMatch(StatesGroup):
    number = State()
    type = State()


class FormCurrencyEmissionRequest(StatesGroup):
    number_match = State()
    data_country = State()
    name_currency = State()
    tick_currency = State()
    following_resource = State()
    course_following = State()
    capitalization = State()
    amount_emission_currency = State()
    date_request_creation = State()
    status_confirmed = State()
    date_confirmed = State()
    message_id_delete = State()


