# import StatesGroup
from aiogram.fsm.state import StatesGroup, State


# Класс по регистрации новой семьи
class SingUp(StatesGroup):
    nickname = State()
    country = State()
    region = State()