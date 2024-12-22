from asyncio.log import logger

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

# Импортируйте модули, которые используются внутри функций
import app.DatabaseWork.master as master_db
import app.DatabaseWork.match as match_db

# import keyboards
import app.keyboards.choice_country as kb

from aiogram import Router

router = Router()


@router.callback_query()
async def start_country_menu(callback: CallbackQuery):

    await callback.message.answer('Меню государства открыто.')
