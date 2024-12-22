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

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == 'created_match')
async def start_created_match(callback: CallbackQuery, state: FSMContext):
    """
    Initiates the map creation process by asking the admin to enter a map number.
    """
    await callback.answer(
        'Вы перешли в создание карты.',
        reply_markup=ReplyKeyboardRemove()
    )

    await state.set_state(SG.CreatedMatch.number)

    await callback.message.edit_text(
        'Введите пожалуйста <b>номер карты</b>, которой хотите создать:',
        parse_mode="html"
    )


@router.message(SG.CreatedMatch.number)
async def choice_type_map(message: Message, state: FSMContext):
    """
    Handles the map number input, validates it, and moves to the next step if valid.
    """
    map_number_input = message.text.strip()

    try:
        if not map_number_input.isdigit():
            raise InvalidMatchNumberFormatError('Номер карты должен быть целым числом.')

        if len(map_number_input) != 7:
            raise InvalidMatchNumberFormatError('Номер карты должен состоять ровно из 7 цифр.')

        map_number = int(map_number_input)

        # Check if the map number already exists in the database
        if await master_db.check_number_match_exists(map_number):
            await message.answer(
                '❌ <b>Этот номер карты уже существует</b>. Пожалуйста, введите другой номер.',
                parse_mode="html"
            )
            return

        # Save valid map number and proceed to the next state
        await state.update_data(number=map_number)
        await state.set_state(SG.CreatedMatch.type_map)

        await message.answer(
            'Выберите <b>тип карты</b>:',
            reply_markup=kb.types_map,
            parse_mode="html"
        )

    except InvalidMatchNumberFormatError as error:
        await message.answer(
            f'❌ <b>Неверный формат номера карты.</b> \n{error} Попробуйте снова:',
            parse_mode="html"
        )
    except Exception as error:
        await message.answer(
            '❌ <b>Произошла ошибка при проверке номера карты.</b> Попробуйте еще раз позже.',
            parse_mode="html"
        )
        logger.error(f"Ошибка при проверке номера карты: {error}")


@router.message(lambda message: message.text in ['Великая война'], SG.CreatedMatch.type_map)
async def set_map_type(message: Message, state: FSMContext):
    """
    Saves the chosen map type and provides a summary to the user.
    """
    await state.update_data(type_map=message.text)
    data_created_match = await state.get_data()

    # Temporary message for processing
    send_message = await message.answer("Обработка...",
                                        reply_markup=ReplyKeyboardRemove(),
                                        parse_mode="html")

    await delete_message(message.bot, message.chat.id, send_message.message_id)

    await message.answer(
        '<b>Информация о созданной карте</b>'
        f'\n№ карты: {data_created_match["number"]}'
        f'\nТип: {data_created_match["type_map"]}',
        reply_markup=kb.confirm_created_map,
        parse_mode="html"
    )


@router.callback_query(F.data == 'confirm_creation')
async def confirm_map_creation(callback: CallbackQuery, state: FSMContext):
    """
    Confirms the creation of the map and triggers the database creation process.
    """
    await callback.message.edit_text(
        'Запускаем создание необходимой среды для вашей карты.',
        parse_mode="html"
    )

    data_created_match = await state.get_data()

    try:
        await master_db.created_match(data_created_match['number'], data_created_match['type_map'])

        await state.clear()

        await callback.message.edit_text(
            f'<b>Необходимая среда для карты</b> {data_created_match["number"]} <b>создана.</b>',
            parse_mode="html"
        )
    except Exception as error:
        await callback.message.edit_text(
            '❌ <b>Произошла ошибка при создании среды для карты.</b> Попробуйте еще раз позже.',
            parse_mode="html"
        )
        logger.error(f"Ошибка при создании карты: {error}")


@router.callback_query(F.data == "restart_creation")
async def restart_map_creation(callback: CallbackQuery, state: FSMContext):
    """
    Restarts the map creation process.
    """
    await state.clear()
    await start_created_match(callback, state)
