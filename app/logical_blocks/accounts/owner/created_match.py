from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

# Import required modules
import ClassesStatesMachine.SG as SG
from ClassesStatesMachine.SG import update_state
from app.MyException import InvalidMatchNumberFormatError

from app.DatabaseWork.models_master import UserManager, MatchesManager
from app.DatabaseWork.models_match import MatchManager

from app import Data_type_map

from app.decorators.message import MessageManager
from app.keyboards.accounts.owner import created_match as kb
from app.utils import callback_utils


logger = logging.getLogger(__name__)

router = Router()
user_manager = UserManager()
matches_manager = MatchesManager()
match_manager = MatchManager()

PREFIXES = {
    "SETTING": "SettingsMatсhes",
    "CREATED": "CreatedMatch",
    "DELETED": "DeletedMatch",
    "CATEGORY": "CategoryMatch",
    "TYPE_MAP": "TypeMap"
}

OWNER_ID = '5311154389'

# 🔹 Шаблоны текстов шагов
STEP_TEXTS = {
    1: "<b>Введите номер матча:</b>\n{data_form}",
    2: "<b>Выберите категорию матча:</b>\n{data_form}",
    3: "<b>Выберите ID Владельца матча:</b>\n{data_form}",
    4: "<b>Выберите тип карты для матча:</b>\n{data_form}",
    5: "<b>Выберите действие:</b>\n{data_form}"
}


async def send_match_step(callback, state, step: int, **kwargs):
    """Отправка сообщения для каждого шага создания матча."""
    message_manager = MessageManager(bot=callback.bot, state=state)
    data_form = await state.get_data()

    # Обновляем параметры
    for key, value in kwargs.items():
        if value is not None:
            data_form[key] = value

    owner_match = '' if step < 3 else ('My' if data_form.get('id_user_owner_match') == OWNER_ID else 'Partner')

    # Формируем общий текст этапов с выделением текущего этапа жирным шрифтом
    steps_text = (
        f"{step}/5 ЭТАП\n"
        f"{'<b>1 Этап - № Матча:</b>' if step == 1 else '1 Этап - № Матча:'} {data_form.get('number_match', '')}\n"
        f"{'<b>2 Этап - Категория:</b>' if step == 2 else '2 Этап - Категория:'} {owner_match}\n"
        f"3 Этап - ID Владельца матча: {data_form.get('id_user_owner_match', '')}\n"
        f"{'<b>4 Этап - Тип карты:</b>' if step == 4 else '4 Этап - Тип карты:'} {data_form.get('type_map', '')}\n"
        f"{'<b>5 Этап - Подтверждение создания:</b>' if step == 5 else '5 Этап - Подтверждение создания:'}\n\n"
    )

    # Собираем сообщение
    text = f"{steps_text}{STEP_TEXTS.get(step, '!Неизвестно! на каком вы этапе?').format(data_form=data_form)}"
    keyboard = await kb.created_match_step(number_step=step)

    await message_manager.send_photo(
        obj=callback,
        text=text,
        keyboard=keyboard,
        remove_previous=True
    )


@router.callback_query(lambda c: c.data and c.data.startswith(f'{PREFIXES['SETTING']}_'))
async def setting_matches_for_owner(callback: CallbackQuery, state: FSMContext):
    """Меню настройки матчей для Владельца"""
    await callback.answer()

    event = callback_utils.parse_callback_data(callback.data, PREFIXES["SETTING"])[0]
    message_manager = MessageManager(bot=callback.bot, state=state)
    keyboard = await kb.menu_setting_matches()

    await message_manager.send_photo(
        obj=callback,
        text='<b>Настройки матча</b>',
        keyboard=keyboard,
        remove_previous=True,
        clear_state_all_exception_photo_message_id=True if event == 'back' else False
    )


@router.callback_query(F.data == f'{PREFIXES['CREATED']}')
async def start_created_match(callback: CallbackQuery, state: FSMContext):
    """Инициирует процесс создания матча, предлагая ввести номер матча. 1/4 этапов"""
    await state.set_state(SG.FormCreatedMatch.number_match)
    await send_match_step(callback, state, 1)


@router.message(SG.FormCreatedMatch.number_match)
async def created_match(message: Message, state: FSMContext):
    """Выбор категории матча. 2/4 этапов"""
    input_number_match = message.text.strip()

    try:
        if not input_number_match.isdigit() or len(input_number_match) != 7:
            raise InvalidMatchNumberFormatError('Номер матча должен быть целым числом, состоящим из ровно 7 цифр.')

        input_number_match = int(input_number_match)

        if await matches_manager.match_exists(number_match=input_number_match):
            raise InvalidMatchNumberFormatError('Этот номер матча уже существует')

        await update_state(state, number_match=input_number_match)
        await state.set_state(SG.FormCreatedMatch.id_user_owner_match)
        await send_match_step(message, state, 2, number_match=input_number_match)

    except InvalidMatchNumberFormatError as error:
        await callback_utils.handle_exception(message,
        'choice_type_match', error,
        '❌<b>Неверный формат номера матча.</b> Попробуйте еще раз.'
        )
        return


@router.callback_query(lambda c: c.data and c.data.startswith(f'{PREFIXES['CATEGORY']}_'))
async def choice_owner_match(callback: CallbackQuery, state: FSMContext):
    """Проверка выбора категории матча. 2/4 этапов"""
    id_user_owner_match = callback_utils.parse_callback_data(callback.data, PREFIXES["CATEGORY"])[0]
    if id_user_owner_match == 'my':
        await choice_my_owner_match(callback=callback, state=state)
    elif id_user_owner_match == 'partner':
        await choice_partner_owner_match(message=callback.message, state=state)


async def choice_my_owner_match(callback: CallbackQuery, state: FSMContext):
    """Выбор владельца матча. 3/4 этапов. Выбрали - My"""
    await update_state(state, id_user_owner_match=OWNER_ID)
    await state.set_state(SG.FormCreatedMatch.type_map)
    await send_match_step(callback, state, 4, id_user_owner_match=OWNER_ID)


async def choice_partner_owner_match(message: Message, state: FSMContext):
    """Выбор владельца матча. 3/4. Выбрали - Partner"""
    message_manager = MessageManager(bot=message.bot, state=state)

    await message_manager.send_photo(
        obj=message,
        text='<b>Введите одно из данных Владельца матча: first_name, last_name, username, telegram_id</b>',
        remove_previous=True
    )


@router.message(SG.FormCreatedMatch.id_user_owner_match)
async def partner_owner_match(message: Message, state: FSMContext):
    """Проверка выбора владельца матча. 3/4. Ввели данные - Partner"""
    search_parameter_owner_match = message.text.strip()

    data_user = None

    if search_parameter_owner_match.isdigit():
        telegram_id = int(search_parameter_owner_match)
        logger.info("📶 Введён числовой идентификатор (Telegram ID)")
        data_user = await user_manager.get_user(telegram_id=telegram_id)

    else:
        for field in ["first_name", "last_name", "username"]:
            logger.info(f'📶 get_user from partner_owner_match: trying {field}')
            data_user = await user_manager.get_user(**{field: search_parameter_owner_match})

            if data_user:
                break

    if data_user:
        id_user_owner_match = data_user['telegram_id']
        await update_state(state, id_user_owner_match=id_user_owner_match)
        await state.set_state(SG.FormCreatedMatch.type_map)
        await send_match_step(message, state, 4, id_user_owner_match=id_user_owner_match)

    else:
        logger.info("📶 Пользователь не найден")
        await choice_partner_owner_match(message=message, state=state)


@router.callback_query(lambda c: c.data and c.data.startswith(f'{PREFIXES['TYPE_MAP']}_'))
async def choice_type_map(callback: CallbackQuery, state: FSMContext):
    """Выбор типа карты. 4/4 этапов."""
    input_type_map = callback_utils.parse_callback_data(callback.data, PREFIXES["TYPE_MAP"])[0]
    await update_state(state, type_map=input_type_map)
    await send_match_step(callback, state, 5, type_map=input_type_map)


@router.callback_query(F.data == 'confirm_creation')
async def confirm_match_creation(callback: CallbackQuery, state: FSMContext):
    """Подтверждает создание матча и записывает его в базу данных."""
    try:
        message_manager = MessageManager(bot=callback.message.bot, state=state)

        await message_manager.send_photo(
            obj=callback,
            text='Запускаем создание необходимой среды для вашего матча.',
            remove_previous=True
        )

        data_created_match = await state.get_data()

        if data_created_match is None:
            await start_created_match(callback, state)

        number_match = data_created_match['number_match']
        id_user_owner_match = data_created_match['id_user_owner_match']
        type_map = data_created_match['type_map']

        try:

            created_num = await matches_manager.create_match(
                number_match=number_match,
                id_user_owner_match=id_user_owner_match,
                type_map=type_map
            )

            if not created_num:
                raise Exception("Ошибка: матч не был записан в master.db!")

            if type_map == 'ВеликаяВойна':
                type_map = Data_type_map.The_Great_War
            elif type_map == 'ВойнаВОгне':
                type_map = Data_type_map.War_in_Fire
            else:
                Exception('Ошибка: Type_map пуст.')

            await match_manager.initialize_match(
                number_match=number_match,
                id_user_owner_match=id_user_owner_match,
                type_map=type_map
            )
        except Exception as error:
            await callback.message.answer(str(error))

        message_manager = MessageManager(bot=callback.message.bot, state=state)

        await message_manager.send_photo(
            obj=callback,
            text=f'<b>Необходимая среда для матча:</b> {data_created_match["number_match"]} <b>создана.</b>',
            remove_previous=True,
            clear_state_all_exception_photo_message_id=True
        )
    except Exception as error:
        await callback_utils.handle_exception(callback, 'confirm_match_creation', error, '❌ Произошла ошибка при создании среды для матча. Попробуйте позже.')


@router.callback_query(F.data == "restart_creation")
async def restart_match_creation(callback: CallbackQuery, state: FSMContext):
    """Перезапускает процесс создания матча, удаляя все параметры state, кроме photo_message_id."""

    # Получаем данные из state
    state_data = await state.get_data()

    # Сохраняем photo_message_id, если он есть
    photo_message_id = state_data.get("photo_message_id")

    # Очищаем state
    await state.clear()

    # Восстанавливаем только photo_message_id
    if photo_message_id is not None:
        await state.update_data(photo_message_id=photo_message_id)

    # Запускаем процесс создания матча
    await start_created_match(callback, state)

