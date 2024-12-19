# import StatesGroup
from aiogram.fsm.state import StatesGroup, State


# Класс по регистрации новой семьи
class SingUp(StatesGroup):
    nickname = State()
    country = State()
    region = State()


class CreatedMatch(StatesGroup):
    number = State()
    type_map = State()


# Определите состояния для хранения message_id
class Form(StatesGroup):
    photo_message_id = State()
