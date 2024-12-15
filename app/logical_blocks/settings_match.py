from aiogram import F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

# Импортируйте модули, которые используются внутри функций
import ClassesStatesMachine.SG as SG
import app.DatabaseWork.master as master_db
import app.keyboards as kb

from app.message_designer.message_in_chat import delete_message

from aiogram import Router

router = Router()


@router.callback_query(F.data == 'settings_match')
async def start(callback : CallbackQuery, state : FSMContext):
    pass