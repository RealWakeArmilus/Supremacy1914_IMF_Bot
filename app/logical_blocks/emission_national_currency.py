from datetime import datetime
import pytz

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
import logging

# import keyboards
import ClassesStatesMachine.SG as SG
import app.DatabaseWork.master as master_db
import app.DatabaseWork.match as match_db
import app.keyboards.emission_national_currency as kb
from app.message_designer.formatzer import format_large_number
from app.message_designer.deletezer import delete_message
from app.utils import callback_utils

logger = logging.getLogger(__name__)

# Router setup
router = Router()


START_EMISSION_NATIONAL_CURRENCY = 'StartEmissionNationalCurrency'
AMOUNT_EMISSION_NAT_CURRENCY = 'AmountEmissionNatCurrency'


@router.callback_query(lambda c: c.data and c.data.startswith(f'{START_EMISSION_NATIONAL_CURRENCY}_'))
async def start_emission_national_currency(callback: CallbackQuery, state: FSMContext, number_match: str = None):

    try:
        if number_match is None:
            try:
                parse_number_match = callback_utils.parse_callback_data(callback.data, START_EMISSION_NATIONAL_CURRENCY)[0]
                number_match = parse_number_match
            except (IndexError, TypeError) as error:
                await callback_utils.handle_error(callback, error, 'Ошибка при разборе запуске формы эмиссии нац. валюты. ')
                return

        await callback_utils.notify_user(callback, f'Заполнение бланка "эмиссии национальной валюты" для матча: {number_match}')

        await state.set_state(SG.FormCurrencyEmissionRequest.number_match)
        await state.update_data(number_match=number_match)
        logger.info(f"Updated FSMContext with number_match: {number_match}")

        await state.set_state(SG.FormCurrencyEmissionRequest.telegram_id)
        await state.update_data(telegram_id=callback.from_user.id)
        logger.info(f"Updated FSMContext with telegram_id: {callback.from_user.id}")

        data_country = await match_db.get_data_country(callback.from_user.id, number_match)
        if not data_country:
            raise ValueError("Не удалось получить данные страны.")

        await state.set_state(SG.FormCurrencyEmissionRequest.country_id)
        await state.update_data(country_id=data_country['country_id'])
        logger.info(f"Updated FSMContext with country_id: {data_country['country_id']}")

        await state.set_state(SG.FormCurrencyEmissionRequest.name_currency)

        await callback_utils.send_edit_message(callback,
            f'<b>№ матча:</b> {number_match}\n'
            f'<b>Ваше государство:</b> {data_country['name_country']}\n\n'
            '<i>Правила названия валюты:</i>\n'
            '<blockquote>'
            '1. Не менее 3-х символов\n'
            '2. Не более 8-ти символов\n'
            '3. Русскими или английскими буквами\n'
            '4. Исключить числовые значения и знаки\n'
            '5. Исключить матерные слова.'
            '</blockquote>\n\n'
            '<b>Придумайте и введите название вашей валюты:</b>'
        )
    except Exception as error:
        logger.error(f"Error in start_emission_national_currency: {error}", exc_info=True)
        await callback.answer("Произошла ошибка. Пожалуйста, повторите позже.", show_alert=True)



@router.message(SG.FormCurrencyEmissionRequest.name_currency)
async def input_tick_for_emission_national_currency(message: Message, state: FSMContext):
    """
    Проверка введенного имени валюты и ввод тикера валюты
    """
    input_name_currency = message.text.strip()

    try:
        if not input_name_currency.isalpha():
            raise Exception('Ваше название валюты содержит числовые значения или другие знаки.')
        elif len(input_name_currency) > 8:
            raise Exception('Ваше название валюты имеет больше 8-ти символов.')
        elif len(input_name_currency) < 3:
            raise Exception('Ваше название валюты имеет меньше 3-х символов.')

        data_currency_emission_request = await state.get_data()
        number_match = data_currency_emission_request['number_match']
        if not number_match:
            raise KeyError("Ключ 'number_match' отсутствует в данных FSMContext.")

        if await match_db.check_name_currency_exists(number_match, input_name_currency):
            await message.answer(
                f'❌ <b>Название валюты <i>{input_name_currency}</i> уже занято.</b>\n Пожалуйста, придумайте другое.',
                parse_mode="html"
            )
            return

        await state.update_data(name_currency=input_name_currency)
        await state.set_state(SG.FormCurrencyEmissionRequest.tick_currency)
        logger.info(f"Updated FSMContext with name_currency: {input_name_currency}")

        data_country = await match_db.get_data_country(message.from_user.id, number_match)
        if not data_country:
            raise ValueError("Не удалось получить данные страны.")

        await message.answer(
            f'<b>№ матча:</b> {number_match}\n'
            f'<b>Ваше государство:</b> {data_country['name_country']}\n\n'
            '<i>Правила названия тикера:</i>\n'
            '<blockquote>'
            '1. Состоять ровно из 3-х символов\n'
            '2. Только английскими буквами\n'
            '3. Исключить числовые значения и знаки\n'
            '4. Тикер должен читаться коротко, но понятно, чтобы сразу стало ясно о какой валюте идет речь.\n'
            '</blockquote>\n'
            '<b>Придумайте и введите тикер вашей валюты:</b>',
            parse_mode="html"
        )

    except Exception as error:
        await message.answer(
            f'❌ <b>Неверный формат названия валюты.</b> \n{error} Пожалуйста, придумайте другое.',
            parse_mode="html"
        )
        logger.error(f"<input_tick_for_emission_national_currency>: {error}")


@router.message(SG.FormCurrencyEmissionRequest.tick_currency)
async def input_amount_emission_for_emission_national_currency(message: Message, state: FSMContext):
    """
    Проверка введенного тикера валюты и ввод общего числа эмиссии валюты
    """
    input_tick_currency = message.text.strip()

    try:
        if not input_tick_currency.isalpha():
            raise Exception('Ваш тикер валюты содержит числовые значения или другие знаки.')
        if len(input_tick_currency) != 3:
            raise Exception('Ваш тикер валюты не равен 3-м символам.')

        data_currency_emission_request = await state.get_data()
        number_match = data_currency_emission_request['number_match']

        if await match_db.check_tick_currency_exists(number_match, input_tick_currency):
            await message.answer(
                f'❌ <b>Название тикера <i>{input_tick_currency}</i> уже занято.</b>\n Пожалуйста, придумайте другое.',
                parse_mode="html"
            )
            return

        await state.update_data(tick_currency=input_tick_currency)
        await state.set_state(SG.FormCurrencyEmissionRequest.amount_emission_currency)

        data_country = await match_db.get_data_country(message.from_user.id, number_match)

        await message.answer(
            f'<b>№ матча:</b> {number_match}\n'
            f'<b>Ваше государство:</b> {data_country['name_country']}\n\n'
            '<i>Стартовая эмиссия национальной валюты</i>'
            '<blockquote>'
            'Это самый первый выпуск ваших денежных единиц. Когда вы вводите свою валюту в обращение.\n'
            '</blockquote>\n'
            '<i>Стартовый курс вашей валюты</i>'
            '<blockquote>'
            'Так как это ваша первая эмиссия, то идет стандартный расчет: 100.000 (сто тысяч) единиц = 1 серебру'
            '</blockquote>\n\n'
            '<b>Выберите желаемый объем эмиссии (выпуска) вашей национальной валюты:</b>',
            reply_markup=await kb.choice_amount_emission_national_currency(number_match),
            parse_mode="html"
        )
    except Exception as error:
        await message.answer(
            f'❌ <b>Неверный формат тикера валюты.</b> \n{error} Пожалуйста, придумайте другое.',
            parse_mode="html"
        )
        logger.error(f"<input_emission_for_emission_national_currency>: {error}")


@router.callback_query(lambda c: c.data and c.data.startswith(f'{AMOUNT_EMISSION_NAT_CURRENCY}_'))
async def end_emission_national_currency(callback: CallbackQuery, state: FSMContext):

    number_match = callback_utils.parse_callback_data(callback.data, AMOUNT_EMISSION_NAT_CURRENCY)[0]
    amount_emission = callback_utils.parse_callback_data(callback.data, AMOUNT_EMISSION_NAT_CURRENCY)[1]

    try:
        if amount_emission == '5billions':
            amount_emission = 5000000000
        elif amount_emission == '10billions':
            amount_emission = 10000000000
        else:
            raise Exception('Неизвестный выбор объема эмиссии национальной валюты')
    except Exception as error:
        await callback_utils.handle_error(callback, error, 'Ошибка при вводе объема эмиссии валюты.')

    await state.update_data(amount_emission_currency=amount_emission)
    await state.set_state(SG.FormCurrencyEmissionRequest.capitalization)

    capitalization = amount_emission // 100000

    await state.update_data(capitalization=capitalization)
    await state.set_state(SG.FormCurrencyEmissionRequest.date_request_creation)

    timezone = pytz.timezone("Europe/Moscow")
    now_date = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")

    await state.update_data(date_request_creation=now_date)
    await state.set_state(SG.FormCurrencyEmissionRequest.status_confirmed)
    await state.update_data(status_confirmed=False)
    await state.set_state(SG.FormCurrencyEmissionRequest.date_confirmed)
    await state.update_data(date_confirmed='')

    data_request_emission_national_currency = await state.get_data()
    data_country = await match_db.get_data_country(callback.from_user.id, number_match)

    sent_message = await callback_utils.send_edit_message(callback,
        f'<b>№ матча:</b> {number_match}\n'
        f'<b>Ваше государство:</b> {data_country['name_country']}\n'
        f'<b>Дата заявки:</b> {data_request_emission_national_currency['date_request_creation']}\n\n'
        '<i>Проверьте правильно ли заполнены данные, по вашей валюты:</i>'
        '<blockquote>'
        f'<b>Название:</b> {data_request_emission_national_currency['name_currency']}\n'
        f'<b>Тикер:</b> {data_request_emission_national_currency['tick_currency']}\n'
        f'<b>Объем эмиссии:</b> {format_large_number(data_request_emission_national_currency['amount_emission_currency'])} единиц\n'
        f'<b>Капитализация:</b> {format_large_number(data_request_emission_national_currency['capitalization'])} серебра\n'
        '</blockquote>\n\n',
        await kb.end_emission_national_currency(number_match)
    )

    await state.set_state(SG.FormCurrencyEmissionRequest.message_id_delete)
    await state.update_data(message_id_delete=sent_message)


@router.callback_query(F.data == 'ConfirmFormEmissionNatCurrency')
async def confirm_form_emission_national_currency(callback: CallbackQuery, state: FSMContext):

    data_request_emission_national_currency = await state.get_data()

    await match_db.save_currency_emission_request(data_request_emission_national_currency)

    instructions = (
        f"<b>Следуйте этой инструкции, для подтверждения вашей эмиссии:</b>\n"
        f"<blockquote>"
        f"1. <b>Откройте игру:</b> Supremacy1914\n"
        f"2. <b>Войдите в матч под номером:</b> {data_request_emission_national_currency['number_match']};\n"
        f"3. <b>Найдите игрока:</b> 'Company Mekas' (он же 'International Monetary Fund');\n"
        f"4. <b>Отправьте сделку:</b> вы переводите {format_large_number(data_request_emission_national_currency['capitalization'])} серебра, в обмен на 1 серебро;\n"
        f"</blockquote>\n"
        f"<b>Пример сделки указан на скрине.</b>\n\n"
        f"<b>Отправьте сделку:</b> вы переводите <b>{format_large_number(data_request_emission_national_currency['capitalization'])}</b> серебра, в обмен на 1 серебро"
    )

    photo_path_1_exemple_transaction_emission_photo_path = 'image/1_exemple_transaction_emission_national_currency.jpg'
    photo = FSInputFile(photo_path_1_exemple_transaction_emission_photo_path)

    await delete_message(callback.bot, callback.from_user.id, data_request_emission_national_currency['message_id_delete'])

    sent_message = await callback.message.answer_photo(
        photo,
        instructions,
        parse_mode='html'
    )

    data_country = await match_db.get_data_country(callback.from_user.id, data_request_emission_national_currency['number_match'])

    chat_id_admin = await master_db.get_telegram_id_admin()
    admin_message = (
        f"<i><b>Запрос государства</b> на <b>эмиссию</b> своей <b>нац. валюты</b></i>\n"
        f"<b>Дата заявки:</b> {data_request_emission_national_currency['date_request_creation']}\n\n"
        f"<b>Матч:</b> {data_request_emission_national_currency['number_match']}\n"
        f"<b>Государство:</b> {data_country['name_country']}\n"
        f"<b>Название валюты:</b> {data_request_emission_national_currency['name_currency']}\n"
        f"<b>Тикер валюты:</b> {data_request_emission_national_currency['tick_currency']}\n"
        f"<b>Объем эмиссии:</b> {format_large_number(data_request_emission_national_currency['amount_emission_currency'])} единиц\n"
        f"<b>Капитализация:</b> {format_large_number(data_request_emission_national_currency['capitalization'])} серебра\n\n"
        f"<i>Проверить:</i>\n"
        f"<blockquote>"
        "1. Дату заявки\n"
        "2. Номер матча\n"
        "3. Какое государство сделало запрос на эмиссию нац. валюты\n"
        "4. Содержит ли название валюты матерные слова или символьные дефекты\n"
        "5. Содержит ли тикер валюты русские буквы или символьные дефекты\n"
        "6. Объем эмиссии соответствует капитализации, по курсу 100 000 ед == 1 серебро\n"
        f"</blockquote>"
    )

    admin_decision_message = await callback.bot.send_message(
        chat_id=chat_id_admin,
        text=admin_message,
        reply_markup=await kb.verify_form_emission_national_currency(number_match=data_request_emission_national_currency['number_match']),
        parse_mode="html"
    )

    # TODO сохранить сообщение администрации, чтобы при решении админа сообщение в чате админа удалилось


@router.callback_query(lambda c: c.data and c.data.startswith('RestartFormEmissionNatCurrency_'))
async def restart_form_emission_national_currency(callback: CallbackQuery, state: FSMContext):

    number_match = callback_utils.parse_callback_data(callback.data, 'RestartFormEmissionNatCurrency')[0]

    await state.clear()
    await start_emission_national_currency(callback, state, number_match)
