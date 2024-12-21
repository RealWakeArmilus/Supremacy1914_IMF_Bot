from aiogram import F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

# Импортируйте модули, которые используются внутри функций
import ClassesStatesMachine.SG as SG
import app.DatabaseWork.master as master_db
import app.keyboards.created_match as kb

from app.message_designer.deletezer import delete_message

from aiogram import Router

router = Router()


@router.callback_query(F.data == 'created_match')
async def start_created_match(callback : CallbackQuery, state : FSMContext):

    # transition notification create match
    await callback.answer(
        'Вы перешли в создание карты.',
        reply_markup=ReplyKeyboardRemove())

    # Set the administrator's status to enter the card number
    await state.set_state(SG.CreatedMatch.number)

    # message from callback to bot admin and delete previous bot message
    await callback.message.edit_text(
        'Введите пожалуйста <b>номер карты</b>, которой хотите создать:',
        parse_mode="html")


@router.message(SG.CreatedMatch.number)
async def choice_type_map(message: Message, state: FSMContext):

    map_number_input = message.text.strip()

    map_number : int

    try:

        if not map_number_input.isdigit():

            raise ValueError('Номер карты должен быть целым числом.')

        if len(map_number_input) != 7:

            raise ValueError('Номер карты должен состоять ровно из 7 цифр.')

        map_number = int(map_number_input)

    except ValueError as error:

        # Если введено не число, отправляем сообщение об ошибке
        await message.answer(
            f'❌ <b>Неверный формат номера карты.</b> \n{error} Попробуйте снова:',
            parse_mode="html")

        # We interrupt processing so that the user re-enters the card number
        return

    try:

        check_number = await master_db.check_number_match_exists(map_number)

        # Проверяем, существует ли карта в базе данных
        if check_number:

            await message.answer(
                '❌ <b>Этот номер карты уже существует</b>. Пожалуйста, введите другой номер.',
                parse_mode="html")

            # We interrupt processing so that the user re-enters the card number
            return

        # Если номер карты уникальный, сохраняем его в состоянии
        await state.update_data(number=map_number)
        await state.set_state(SG.CreatedMatch.type_map)

        # Запрашиваем тип карты
        await message.answer(
            'Выберите <b>тип карты</b>:',
            reply_markup=kb.types_map,
            parse_mode="html")

    except Exception as error:

        # Обработка исключений (например, ошибка подключения к базе данных)
        await message.answer(
            '❌ <b>Произошла ошибка при проверке номера карты.</b> Попробуйте еще раз позже.',
            parse_mode="html")

        print(f"Ошибка при проверке номера карты: \n{error}")  # Логируем ошибку


@router.message(lambda message: message.text in ['Великая война'], SG.CreatedMatch.type_map)
async def end(message: Message, state: FSMContext):

    await state.update_data(type_map=message.text)

    data_created_match = await state.get_data()

    send_message = await message.answer("Обработка...",
                         reply_markup=ReplyKeyboardRemove(),
                         parse_mode="html")

    await delete_message(message.bot, message.chat.id, send_message.message_id)

    await message.answer(
        '<b>Информация о созданной карте</b>'
        f'\n№ карты: {data_created_match['number']}'
        f'\nType: {data_created_match['type_map']}',
        reply_markup=kb.confirm_created_map,
        parse_mode="html")


@router.callback_query(F.data == 'confirm_creation')
async def confirm(callback: CallbackQuery, state: FSMContext):

    await callback.message.edit_text(
        'Запускаем создание необходимой среды для вашей карты.',
        parse_mode="html")

    data_created_match = await state.get_data()

    await master_db.created_match(data_created_match['number'], data_created_match['type_map'])

    await state.clear()

    await callback.message.edit_text(
        f'<b>Необходимая среда для карты</b> {data_created_match['number']} <b>создана.</b>',
        parse_mode="html")


@router.callback_query(F.data == "restart_creation")
async def restart(callback: CallbackQuery, state: FSMContext):

    await state.clear()

    # Вызываем функцию start_created_match
    await start_created_match(callback, state)
