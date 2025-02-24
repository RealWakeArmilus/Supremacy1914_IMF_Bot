from aiogram import Router
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import logging

# import keyboards
import app.keyboards.lobby as kb_lobby

# import verify
import app.verify.checks as checks

# import ClassState
from app.decorators.message import MessageManager
from app.config import CHANNEL_USERNAME

# ManagerDatabase
from app.DatabaseWork.models_master import UserManager
from app.DatabaseWork.models_master import MatchesManager
from app.DatabaseWork.models_match import MatchManager

# Для передачи сигнала в данный файл, что запуск команд идет здесь
logger = logging.getLogger(__name__)
router = Router()
user_manager = UserManager()

# import routers from logical_blocks
from app.logical_blocks.accounts.account import router as account_router
from app.logical_blocks.accounts.owner.setting_match import router as created_match_router
from app.logical_blocks.settings_match import router as settings_match_router
from app.logical_blocks.choice_country import router as choice_state_router

# connect routers from logical_blocks
router.include_router(account_router)
router.include_router(created_match_router)
router.include_router(settings_match_router)
router.include_router(choice_state_router)


@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    if message.chat.type != 'private' or message.from_user.is_bot:
        return

    user_id = message.from_user.id

    logger.info('📶get_user from /start: connect')

    get_user_task = user_manager.get_user(telegram_id=user_id)
    is_subscribed_task = checks.identify_subscription(bot=message.bot, user_id=user_id)

    data_user = await get_user_task
    is_subscribed = await is_subscribed_task

    if data_user is None:
        text = (
            '<b>Используя бот вы соглашаетесь соблюдать следующие условия:</b>\n\n'
            '<i><a href="ссылка">Пользовательское соглашение</a></i>\n'
            '<i><a href="ссылка">Политика конфиденциальности</a></i>'
        )
        await message.answer(
            text=text,
            parse_mode='html'
        )

        logger.info('📶set_user from /start: connect')
        await user_manager.set_user(
            telegram_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            start_premium=None,
            end_premium=None,
            count_premium=0
        )

    # Проверяем подписку перед взаимодействием с БД
    if not is_subscribed:
        text = (
            "Продолжай быть в курсе событий нашего проекта - подпишись на наш телеграмм канал "
            "<b>Supremacy1914_IMF_Channel</b> 😉💫\n\n"
            "Мы тут общаемся, обсуждаем нововведения и находим новых друзей или команду!\n\n"
            "Присоединяйся по ссылке: https://t.me/Supremacy1914_IMF_Channel ✨\n\n"
            "<b>Чтобы продолжить необходимо подписаться</b>\n\n"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Подписаться", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton(text="Продолжить", callback_data="check_sub")]
        ])

        await message.answer(text=text, reply_markup=keyboard, parse_mode='html')
        return

    await menu_open(message, state)


@router.callback_query(lambda c: c.data == "check_sub")
async def check_sub_again(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки "Я подписался"""
    user_id = callback.from_user.id
    is_subscribed = await checks.identify_subscription(
        bot=callback.message.bot,
        user_id=user_id
    )

    if is_subscribed:
        await menu_open(callback.message, state)
    else:
        await callback.answer("❌ Вы еще не подписались!", show_alert=True)


@router.callback_query(lambda c: c.data == "menu")
async def check_sub_again(callback: CallbackQuery, state: FSMContext):
    await menu_open(message=callback.message, state=state)


@router.message(Command('menu'))
async def menu_open(message: Message, state: FSMContext):
    user_id = message.from_user.id
    is_subscribed = await checks.identify_subscription(
        bot=message.bot,
        user_id=user_id
    )

    if is_subscribed:
        photo_path = 'image/logo.png'
        keyboard = await kb_lobby.main_lobby()

        # Используем класс MessageManager для отправки сообщения
        message_manager = MessageManager(bot=message.bot, state=state)
        await message_manager.send_photo(
            obj=message,
            photo_path=photo_path,
            keyboard=keyboard,
            remove_previous=True
        )
