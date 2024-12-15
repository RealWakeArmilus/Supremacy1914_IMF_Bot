from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message

# import keyboards
import app.keyboards as kb
import app.verication.admin as admin

# Для передачи сигнала в данный файл, что запуск команд идет здесь
router = Router()

from app.logical_blocks.created_match import router as created_match_router
from app.logical_blocks.settings_match import router as settings_match_router

router.include_router(created_match_router)
router.include_router(settings_match_router)


@router.message(Command('admin'))
async def cmd_admin(message: Message):

    status_type_user = await admin.verify(message.chat.type, message.chat.id, message.from_user.id)

    if status_type_user == admin.Status.TypeUser.ADMIN:

        await message.answer(
            f'Здравствуйте администратор {message.from_user.full_name}.',
            reply_markup=kb.admin_menu, parse_mode='html')

    elif status_type_user == admin.Status.TypeUser.SIMPLE:

        await message.answer('Вы не являетесь администратором.')

    else:

        pass
