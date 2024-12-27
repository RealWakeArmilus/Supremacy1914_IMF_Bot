from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import logging

# Import required modules
import ClassesStatesMachine.SG as SG
import app.DatabaseWork.master as master_db
import app.keyboards.created_match as kb
from app.message_designer.deletezer import delete_message
from app.MyException import InvalidMatchNumberFormatError
from app.utils import callback_utils

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == 'created_match')
async def start_created_match(callback: CallbackQuery, state: FSMContext):
    """
    Initiates the map creation process by asking the admin to enter a map number.
    /nИнициирует процесс создания матча, предлагая администратору ввести номер матча.
    """
    await callback_utils.notify_user(callback, 'Вы перешли в создание матча.')

    await state.set_state(SG.FormCreatedMatch.number)

    await callback_utils.send_edit_message(callback,
        '<b>Введите номер матча, который хотите создать</b>:'
    )

@router.message(SG.FormCreatedMatch.number)
async def choice_type_match(message: Message, state: FSMContext):
    """
    Handles the map number input, validates it, and moves to the next step if valid.
    /nОбрабатывает введенный номер матча, проверяет его и переходит к следующему шагу, если он действителен.
    """
    input_number_match = message.text.strip()

    try:
        if not input_number_match.isdigit():
            raise InvalidMatchNumberFormatError('Номер матча должен быть целым числом.')

        if len(input_number_match) != 7:
            raise InvalidMatchNumberFormatError('Номер матча должен состоять ровно из 7 цифр.')

        number_match = int(input_number_match)

        # Check if the map number already exists in the database
        if await master_db.check_number_match_exists(number_match):
            await message.answer(
                '❌ <b>Этот номер матча уже существует</b>. Пожалуйста, введите другой номер.',
                parse_mode="html"
            )
            return

        # Save valid map number and proceed to the next state
        await state.update_data(number=number_match)
        await state.set_state(SG.FormCreatedMatch.type)

        await message.answer(
            'Выберите <b>тип матча</b>:',
            reply_markup=kb.types_match,
            parse_mode="html"
        )

    except InvalidMatchNumberFormatError as error:
        await message.answer(
            f'❌ <b>Неверный формат номера матча.</b> \n{error} Попробуйте снова:',
            parse_mode="html"
        )
    except Exception as error:
        await message.answer(
            '❌ <b>Произошла ошибка при проверке номера матча.</b> Попробуйте еще раз позже.',
            parse_mode="html"
        )
        logger.error(f"Error <Created_match/choice_type_match>: {error}")


@router.message(lambda message: message.text in ['Великая война'], SG.FormCreatedMatch.type)
async def set_type_match(message: Message, state: FSMContext):
    """
    Saves the chosen map type and provides a summary to the user.
    /nСохраняет выбранный тип матча и предоставляет пользователю сводку.
    """
    await state.update_data(type_match=message.text)
    data_created_match = await state.get_data()

    # Temporary message for processing
    send_message = await message.answer("Обработка...",
                                            reply_markup=ReplyKeyboardRemove(),
                                            parse_mode="html")

    await delete_message(message.bot, message.chat.id, send_message.message_id)

    await message.answer(
        '<b>Информация матча</b>'
        f'\n№ матча: {data_created_match["number"]}'
        f'\nТип: {data_created_match["type_match"]}',
        reply_markup=kb.confirm_created_match,
        parse_mode="html"
    )

@router.callback_query(F.data == 'confirm_creation')
async def confirm_match_creation(callback: CallbackQuery, state: FSMContext):
    """
    Confirms the creation of the map and triggers the database creation process.
    /nПодтверждает создание матча и запускает процесс создания базы данных.
    """
    await callback_utils.send_edit_message(
        callback,
        'Запускаем создание необходимой среды для вашего матча.'
    )

    data_created_match = await state.get_data()

    try:
        await master_db.created_match(data_created_match['number'], data_created_match['type_match'])

        await state.clear()

        await callback_utils.send_edit_message(
            callback,
            f'<b>Необходимая среда для матча:</b> {data_created_match["number"]} <b>создана.</b>'
        )
    except Exception as error:
        await callback_utils.send_edit_message(
            callback,
            '❌ <b>Произошла ошибка при создании среды для матча.</b> Попробуйте еще раз позже.'
        )
        logger.error(f"Error <Created_match/confirm_match_creation>: {error}")


@router.callback_query(F.data == "restart_creation")
async def restart_match_creation(callback: CallbackQuery, state: FSMContext):
    """
    Restarts the match creation process.
    /nПерезапускает процесс создания матча.
    """
    await state.clear()
    await start_created_match(callback, state)
