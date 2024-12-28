from datetime import datetime
import pytz
import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

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
FOLLOWING_RESOURCE_NAT_CURRENCY = 'FollowingResourceNatCurrency'
RESTART_EMISSION_NAT_CURRENCY = 'RestartFormEmissionNatCurrency'


@router.callback_query(lambda c: c.data and c.data.startswith(f'{START_EMISSION_NATIONAL_CURRENCY}_'))
async def start_emission_national_currency(callback: CallbackQuery, state: FSMContext, number_match: str = None):

    try:
        if number_match is None:
            try:
                parse_number_match = callback_utils.parse_callback_data(callback.data, START_EMISSION_NATIONAL_CURRENCY)[0]
                number_match = parse_number_match
            except (IndexError, TypeError) as error:
                await callback_utils.handle_error(callback, error, 'Ошибка при разборе запуска формы эмиссии нац. валюты. ')
                return

        await callback_utils.notify_user(callback, f'Заполнение бланка "эмиссии национальной валюты" для матча: {number_match}')

        await state.set_state(SG.FormCurrencyEmissionRequest.number_match)
        await state.update_data(number_match=number_match)
        logger.info(f"FSMContext обновлено: number_match={number_match}")

        data_country = await match_db.get_data_country(callback.from_user.id, number_match)
        if not data_country:
            raise ValueError("Не удалось получить данные страны.")

        await state.set_state(SG.FormCurrencyEmissionRequest.data_country)
        await state.update_data(data_country=data_country)
        logger.info(f"FSMContext обновлено: data_country={data_country}")

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
            raise ValueError('Название валюты должно содержать только буквы.')
        if not (3 <= len(input_name_currency) <= 8):
            raise ValueError('Название валюты должно быть от 3 до 8 символов.')

        data_form_emission_currency_request = await state.get_data()
        number_match = data_form_emission_currency_request['number_match']
        if not number_match:
            raise KeyError("Ключ 'number_match' отсутствует в данных FSMContext.")

        if await match_db.check_name_currency_exists(number_match, input_name_currency):
            await message.answer(
                f'❌ <b>Название валюты <i>{input_name_currency}</i> уже занято.</b>\n Пожалуйста, придумайте другое.',
                parse_mode="html"
            )
            return

        await state.update_data(name_currency=input_name_currency)
        logger.info(f"FSMContext обновлено: name_currency={input_name_currency}")

        await state.set_state(SG.FormCurrencyEmissionRequest.tick_currency)

        data_country = data_form_emission_currency_request['data_country']
        if not data_country:
            raise ValueError("Не удалось получить данные страны.")

        await message.answer(
            f'<b>№ матча:</b> {number_match}\n'
            f'<b>Ваше государство:</b> {data_country['name_country']}\n\n'
            '<i>Правила названия тикера:</i>\n'
            '<blockquote>'
            '1. Состоять ровно из 3-х символов.\n'
            '2. Содержать только буквы.\n'
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
        logger.error(f"Ошибка в input_tick_for_emission_national_currency: {error}")


@router.message(SG.FormCurrencyEmissionRequest.tick_currency)
async def input_following_resource_for_emission_national_currency(message: Message, state: FSMContext):
    """
    Проверка введенного тикера валюты и выбор ресурса за которым будет закреплена валюта
    """
    input_tick_currency = message.text.strip().upper()

    try:
        if not input_tick_currency.isalpha():
            raise Exception('Тикер валюты должен содержать только буквы.')
        if len(input_tick_currency) != 3:
            raise Exception('Тикер валюты должен состоять ровно из 3-х символов.')

        data_currency_emission_request = await state.get_data()
        data_country = data_currency_emission_request['data_country']
        number_match = data_currency_emission_request['number_match']

        if await match_db.check_tick_currency_exists(number_match, input_tick_currency):
            await message.answer(
                f'❌ <b>Название тикера <i>{input_tick_currency}</i> уже занято.</b>\n Пожалуйста, придумайте другое.',
                parse_mode="html"
            )
            return

        await state.update_data(tick_currency=input_tick_currency)
        logger.info(f"FSMContext обновлено: tick_currency={input_tick_currency}")

        await state.set_state(SG.FormCurrencyEmissionRequest.following_resource)

        await message.answer(
            f'<b>№ матча:</b> {number_match}\n'
            f'<b>Ваше государство:</b> {data_country["name_country"]}\n\n'
            '<i>Выберите ресурс, за ценой которого будет закреплена ваша валюта:</i>\n',
            reply_markup=await kb.choice_following_resource_national_currency(number_match),
            parse_mode="html"
        )
    except Exception as error:
        await message.answer(
            f'❌ <b>Неверный формат тикера валюты.</b>\n{error}\nПожалуйста, придумайте другой.',
            parse_mode="html"
        )
        logger.error(f"Ошибка в input_following_resource_for_emission_national_currency: {error}")


@router.callback_query(lambda c: c.data and c.data.startswith(f'{FOLLOWING_RESOURCE_NAT_CURRENCY}_'))
async def input_course_following_for_emission_national_currency(callback: CallbackQuery, state: FSMContext):
    """
    Проверка ввода ресурса сопровождения и ввод курс соотношения между нац. валютой и закрепленным за ним ресурсом.
    """
    try:
        number_match = callback_utils.parse_callback_data(callback.data, FOLLOWING_RESOURCE_NAT_CURRENCY)[0]
        following_resource = callback_utils.parse_callback_data(callback.data, FOLLOWING_RESOURCE_NAT_CURRENCY)[1]

        await state.update_data(following_resource=following_resource)
        logger.info(f"FSMContext обновлено: following_resource={following_resource}")

        await state.set_state(SG.FormCurrencyEmissionRequest.course_following)

        data_currency_emission_request = await state.get_data()
        data_country = data_currency_emission_request['data_country']

        await callback_utils.send_edit_message(callback,
            f'<b>№ матча:</b> {number_match}\n'
            f'<b>Ваше государство:</b> {data_country["name_country"]}\n\n'
            f'<b>Введите курс соотношения вашей валюты к закрепленному ресурсу:</b> <i>{following_resource}</i>\n\n'
            '<i>Правила введения курса соотношения:</i>\n'
            '<blockquote>'
                '1. <b>Ваша валюта иметь соотношение:</b> не менее 1 000 ед. валюты к 1 ед. серебра.\n'
                '2. <b>Ваша валюта иметь соотношение:</b> не более 100 000 ед. валюты к 1 ед. серебра.\n'
                '3. <b>При вводе пишите число без пробелов.</b>\n'
                '<b>Целое число</b> <i>- 1000 (тысяча)</i>\n'
                '<b>Не целое число</b> <i>- 1000.55 (тысяча и пятьдесят пять сотых)</i>'
            '</blockquote>\n\n'
            '<b>Введите курс соотношения вашей валюты к закрепленному ресурсу:</b>\n'
            '<blockquote>'
            f'<i>Например, если курс вашей валюты 100 000 единиц = 1 {following_resource}, введите "100000".</i>'
            f'</blockquote>'
        )
    except Exception as error:
        await callback_utils.handle_error(callback, error,
            f'❌ <b>Ошибка на этапе ввода закрепленного ресурса.</b>\n{error}\nПожалуйста, попробуете позже.',
        )
        logger.error(f"Ошибка в input_course_following_for_emission_national_currency: {error}")


@router.message(SG.FormCurrencyEmissionRequest.course_following)
async def input_amount_for_emission_national_currency(message: Message, state: FSMContext):
    """
    Проверка ввода курса валюты к закрепленному ресурсу и ввод объема обеспечения валюты данным ресурсом.
    """
    course_following_input = message.text.strip()

    try:
        course_following = round(float(course_following_input), 2)
        if (course_following < 1000.00) or (course_following > 100000.00):
            raise ValueError('Соотношение между вашей валютой и закрепленного ресурса, должен быть не меньше 1 000,00 и не больше 100 000,00')

        await state.update_data(course_following=course_following)
        logger.info(f"FSMContext обновлено: course_following={course_following}")

        await state.set_state(SG.FormCurrencyEmissionRequest.capitalization)

        data_currency_emission_request = await state.get_data()
        number_match = data_currency_emission_request['number_match']
        data_country = data_currency_emission_request['data_country']

        await message.answer(
            f"<b>№ матча:</b> {number_match}\n"
            f"<b>Ваше государство:</b> {data_country['name_country']}\n\n"
            "<i>Стартовая эмиссия национальной валюты</i>"
            "<blockquote>"
            "Это самый первый выпуск ваших денежных единиц. Когда вы вводите свою валюту в обращение.\n"
            "</blockquote>\n"
            f"<b>Стартовый курс вашей валюты:</b> {format_large_number(data_currency_emission_request['course_following'])}\n\n"
            "<b>Введите сумму сколько вы готовы внести серебра для обеспечения вашей стартовой эмиссии нац. валюты:</b>\n"
            "<i>Правила введения суммы серебра:</i>\n"
            "<blockquote>"
                "При вводе пишите целое число без пробелов.\n\n"
                "Целое число - 10000 (десять тысяч)\n"
                "<b>Не целое число - НЕЛЬЗЯ</b>"
            "</blockquote>",
            parse_mode="html"
        )
    except (Exception, ValueError) as error:
        await message.answer(
            f'❌ <b>Неверный формат курса соотношения.</b> \n{error} Пожалуйста, введите другое значение.',
            parse_mode="html"
        )
        logger.error(f"<input_amount_for_emission_national_currency>: {error}")


@router.message(SG.FormCurrencyEmissionRequest.capitalization)
async def end_emission_national_currency(message: Message, state: FSMContext):

    try:
        input_capitalization = message.text.strip()
        capitalization = int(input_capitalization)

        if capitalization < 50000:
            raise Exception('Объем обеспечения валюты слишком мал. Минимальный порог эмиссии 50 000 серебра.')
        elif capitalization > 500000:
            raise Exception('Объем обеспечения валюты выставлен не реалистично много.')

        await state.update_data(capitalization=capitalization)
        logger.info(f"FSMContext обновлено: capitalization={capitalization}")


        data_currency_emission_request = await state.get_data()

        await state.set_state(SG.FormCurrencyEmissionRequest.amount_emission_currency)
        amount_emission_currency = capitalization * data_currency_emission_request['course_following']
        await state.update_data(amount_emission_currency=amount_emission_currency)
        logger.info(f"FSMContext обновлено: amount_emission_currency={amount_emission_currency}")

        timezone = pytz.timezone("Europe/Moscow")
        now_date = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")

        await state.update_data(date_request_creation=now_date)
        await state.set_state(SG.FormCurrencyEmissionRequest.status_confirmed)
        await state.update_data(status_confirmed=False)
        await state.set_state(SG.FormCurrencyEmissionRequest.date_confirmed)
        await state.update_data(date_confirmed='')

        data_request_emission_national_currency = await state.get_data()
        number_match = data_request_emission_national_currency['number_match']
        date_request_creation = data_request_emission_national_currency['date_request_creation']
        data_country = data_request_emission_national_currency['data_country']
        name_currency = data_request_emission_national_currency['name_currency']
        tick_currency = data_request_emission_national_currency['tick_currency']
        following_resource = data_request_emission_national_currency['following_resource']
        course_following = format_large_number(data_request_emission_national_currency['course_following'])
        amount_emission_currency = format_large_number(data_request_emission_national_currency['amount_emission_currency'])
        capitalization = format_large_number(data_request_emission_national_currency['capitalization'])

        rough_draft_message = (
            f'<b>№ матча:</b> {number_match}\n'
            f'<b>Ваше государство:</b> {data_country['name_country']}\n'
            f'<b>Дата заявки:</b> {date_request_creation}\n\n'
            '<i>Проверьте правильно ли заполнены данные, по вашей валюты:</i>'
            '<blockquote>'
                f"<b>Матч:</b> {data_request_emission_national_currency['number_match']}\n"
                f"<b>Государство:</b> {data_country['name_country']}\n"
                f"<b>Название валюты:</b> {name_currency}\n"
                f"<b>Тикер валюты:</b> {tick_currency}\n"
                f"<b>Валюта закреплена за ресурсом:</b> {following_resource}\n"
                f"<b>Соотношение валюты к ресурсу:</b> {course_following} единиц к 1 {following_resource}\n"
                f"<b>Объем эмиссии:</b> {amount_emission_currency} единиц\n"
                f"<b>Капитализация:</b> {capitalization} серебра\n\n"
            '</blockquote>'
        )

        keyboard = await kb.end_emission_national_currency(data_request_emission_national_currency['number_match'])

        sent_message = await message.answer(rough_draft_message,
                                            reply_markup=keyboard,
                                            parse_mode='html')

        await state.set_state(SG.FormCurrencyEmissionRequest.message_id_delete)
        await state.update_data(message_id_delete=sent_message.message_id)
    except Exception as error:
        await message.answer(f'Ошибка при обработке объема обеспечения валюты: {error}')
        logger.error(f"<end_emission_national_currency>: {error}")


@router.callback_query(F.data == 'ConfirmFormEmissionNatCurrency')
async def confirm_form_emission_national_currency(callback: CallbackQuery, state: FSMContext):
    """
    Подтверждение заполненной формы эмиссии национальной валюты.
    """
    data_request_emission_national_currency = await state.get_data()
    number_match = data_request_emission_national_currency['number_match']
    date_request_creation = data_request_emission_national_currency['date_request_creation']
    data_country = data_request_emission_national_currency['data_country']
    name_currency = data_request_emission_national_currency['name_currency']
    tick_currency = data_request_emission_national_currency['tick_currency']
    following_resource = data_request_emission_national_currency['following_resource']
    course_following = format_large_number(data_request_emission_national_currency['course_following'])
    amount_emission_currency = format_large_number(data_request_emission_national_currency['amount_emission_currency'])
    capitalization = format_large_number(data_request_emission_national_currency['capitalization'])

    # TODO удали print когда он станет не нужным
    print(data_request_emission_national_currency)

    await match_db.save_currency_emission_request(data_request_emission_national_currency)

    instructions = (
        f"<b>Следуйте этой инструкции, для подтверждения вашей эмиссии:</b>\n"
        f"<blockquote>"
        f"1. <b>Откройте игру:</b> Supremacy1914\n"
        f"2. <b>Войдите в матч под номером:</b> {number_match};\n"
        f"3. <b>Найдите игрока:</b> 'Company Mekas' (он же 'International Monetary Fund');\n"
        f"4. <b>Отправьте сделку:</b> вы переводите {capitalization} серебра, в обмен на 1 серебро;\n"
        f"</blockquote>\n"
        f"<b>Пример сделки указан на скрине.</b>\n\n"
        f"<b>Отправьте сделку:</b> вы переводите <b>{capitalization}</b> серебра, в обмен на 1 серебро"
    )

    photo_path_1_exemple_transaction_emission_photo_path = 'image/1_exemple_transaction_emission_national_currency.jpg'
    photo = FSInputFile(photo_path_1_exemple_transaction_emission_photo_path)

    await delete_message(callback.bot, callback.from_user.id, data_request_emission_national_currency['message_id_delete'])

    sent_message = await callback.message.answer_photo(
        photo,
        instructions,
        parse_mode='html'
    )

    chat_id_admin = await master_db.get_telegram_id_admin()
    admin_message = (
        f"<i><b>Запрос государства</b> на <b>эмиссию</b> своей <b>нац. валюты</b></i>\n"
        f"<b>Дата заявки:</b> {date_request_creation}\n\n"
        f"<b>Матч:</b> {number_match}\n"
        f"<b>Государство:</b> {data_country['name_country']}\n"
        f"<b>Название валюты:</b> {name_currency}\n"
        f"<b>Тикер валюты:</b> {tick_currency}\n"
        f"<b>Валюта закреплена за ресурсом:</b> {following_resource}\n"
        f"<b>Соотношение валюты к ресурсу:</b> {course_following} единиц к 1 {following_resource}\n"
        f"<b>Объем эмиссии:</b> {amount_emission_currency} единиц\n"
        f"<b>Капитализация:</b> {capitalization} серебра\n\n"
        f"<i>Проверить:</i>\n"
        f"<blockquote>"
            "1. Дату заявки\n"
            "2. Номер матча\n"
            "3. Какое государство сделало запрос на эмиссию нац. валюты\n"
            "4. Содержит ли название валюты матерные слова или символьные дефекты\n"
            "5. Содержит ли тикер валюты русские буквы или символьные дефекты\n"
            f"6. Объем эмиссии соответствует капитализации, по курсу {course_following} ед. == 1 серебро\n"
        f"</blockquote>"
    )

    admin_decision_message = await callback.bot.send_message(
        chat_id=chat_id_admin,
        text=admin_message,
        reply_markup=await kb.verify_form_emission_national_currency(number_match=data_request_emission_national_currency['number_match']),
        parse_mode="html"
    )

    # TODO сохранить сообщение администрации, чтобы при решении админа сообщение в чате админа удалилось


@router.callback_query(lambda c: c.data and c.data.startswith(f'{RESTART_EMISSION_NAT_CURRENCY}_'))
async def restart_form_emission_national_currency(callback: CallbackQuery, state: FSMContext):
    """
    Перезапуск процесса заполнения формы эмиссии национальной валюты.
    """
    try:
        number_match = callback_utils.parse_callback_data(callback.data, RESTART_EMISSION_NAT_CURRENCY)[0]
        await state.clear()
        await start_emission_national_currency(callback, state, number_match)
    except Exception as error:
        logger.error(f"Ошибка в restart_form_emission_national_currency: {error}", exc_info=True)
        await callback.answer("Не удалось перезапустить форму. Пожалуйста, попробуйте позже.", show_alert=True)
