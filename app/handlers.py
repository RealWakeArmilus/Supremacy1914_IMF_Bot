from aiogram import F, Router
from aiogram.filters.command import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, FSInputFile


# Для передачи сигнала в данный файл, что запуск команд идет здесь
router = Router()

# import keyboards
import app.keyboards as kb

# import StatesClasses, State, FSMContext
import ClassesStatesMachine.SG as SG
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext

# Verification users
import app.verify_user as verify_user


