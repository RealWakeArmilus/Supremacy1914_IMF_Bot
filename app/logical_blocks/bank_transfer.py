from datetime import datetime
import pytz
import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

import ClassesStatesMachine.SG as SG
from ClassesStatesMachine.SG import update_state
from app.DatabaseWork.database import DatabaseManager
from app.keyboards.universal import launch_solution
from app.message_designer.formatzer import format_number
from app.message_designer.deletezer import delete_message
from app.message_designer.chartzer import create_chart_currency_capitals_from_country
from app.utils import callback_utils


# Router setup
router = Router()


logger = logging.getLogger(__name__)


# Callback prefixes
PREFIXES = {
    "START": "StartBankTransfer",
    "BENEFICIARY": "BeneficiaryBankTransfer",
    "CONFIRM": "ConfirmFormBankTransfer",
    "RESTART": "RestartFormBankTransfer",
}


@router.callback_query(lambda c: c.data and c.data.startswith(f'{PREFIXES["START"]}_'))
async def start_bank_transfer(callback: CallbackQuery, state: FSMContext, number_match: str = None):

    try:
        if number_match is None:
            try:
                number_match = number_match or callback_utils.parse_callback_data(callback.data, PREFIXES["START"])[0]
            except (IndexError, TypeError) as error:
                await callback_utils.handle_error(callback, error, 'Ошибка при разборе запуска формы банковские переводы. ')
                return

        await callback_utils.notify_user(callback, f'Заполнение бланка "Банковский перевод" для матча: {number_match}')


        await state.set_state(SG.FormBankTransferRequest.number_match)
        await update_state(state, number_match=number_match)


        data_country = await DatabaseManager(database_path=number_match).get_data_country(
            user_id=callback.from_user.id,
            number_match=number_match
        )

        payer_country_id = data_country['country_id']
        payer_country_name = data_country['name_country']

        await state.set_state(SG.FormBankTransferRequest.payer_country_id)
        await update_state(state, payer_country_id=payer_country_id)

        names_country = await DatabaseManager(database_path=number_match).get_countries_names(busy=True)
        ignor_country_name = payer_country_name

        new_names_country = []

        for name_country in names_country:
            if name_country != ignor_country_name:
                new_names_country.append(name_country)

        if not new_names_country:

            await callback_utils.send_edit_message(callback,
                    text='Список бенефициаров пуст.',
            )

            from app.logical_blocks.country_menu import start_country_menu
            await start_country_menu(callback=callback, number_match=number_match)

        elif new_names_country:

            list_beneficiary = ''

            count_names = 0

            for name_country in new_names_country:
                count_names += 1
                list_beneficiary += f'\n{count_names}. {name_country}'

            text_message = (
                f'<b>№ Матч:</b> {number_match}\n'
                f'<b>Ваше государство:</b> {payer_country_name}\n'
                f'{list_beneficiary}\n\n'
                f'<b>Выберите государство, которому хотите перевести средства, напишите точно как указано в списке.</b>\n'
                f'<b>БЕЗ ПОРЯДКОВОГО НОМЕРА.</b>'
            )

            message_id = await callback_utils.send_edit_message(callback,
                    text=text_message
            )

            await update_state(state, message_id_delete=message_id)

            await state.set_state(SG.FormBankTransferRequest.beneficiary_country_id)

        else:
            raise Exception('Что-то пошло не так.')
    except Exception as error:
        await callback_utils.handle_exception(callback, 'start_bank_transfer', error)


@router.message(SG.FormBankTransferRequest.beneficiary_country_id)
async def input_name_currency_for_bank_transfer(message: Message, state: FSMContext):
    """
    Проверка ввода бенефициара и выбор валюты, которую планируете отправить.
    """
    try:
        # TODO очень похожий код в choice_country/input_name_country_from_number_match_for_user

        input_search_beneficiary_country_name = message.text.strip()
        input_search_beneficiary_country_name = str(input_search_beneficiary_country_name).lower()

        form_choice_country = await state.get_data()
        number_match = form_choice_country['number_match']
        message_id_delete = form_choice_country['message_id_delete']

        names_country = await DatabaseManager(database_path=number_match).get_countries_names(busy=True)

        if not names_country:
            raise ValueError(
                "Не удалось получить список бенефициаров, для сравнения с вашим введенным названием.")

        input_beneficiary_country_name: str = ''

        for name_country in names_country:
            if name_country.lower() == input_search_beneficiary_country_name:
                input_beneficiary_country_name = name_country

        if input_beneficiary_country_name == '':
            raise Exception(
                '\nВведенное названия не найдено в списке бенефициаров.\n\n<b>Повторите свой ввод еще раз</b>')

        await delete_message(
            bot=message.bot,
            message_chat_id=message.chat.id,
            send_message_id=message_id_delete
        )



        beneficiary_country_id = await DatabaseManager(database_path=number_match).get_country_id(country_name=input_beneficiary_country_name)

        if not beneficiary_country_id:
            raise ValueError("Не удалось получить id бенефициара.")

        await update_state(state, beneficiary_country_id=int(beneficiary_country_id))




        data_currency_capitals_from_country = await DatabaseManager(database_path=number_match).get_data_currency_capitals_from_country(
            user_id=message.from_user.id,
            number_match=number_match
        )

        if not data_currency_capitals_from_country:
            raise ValueError("Не удалось получить капитал страны.")

        data_country = await DatabaseManager(database_path=number_match).get_data_country(
            user_id=message.from_user.id,
            number_match=number_match
        )

        if not data_country:
            raise ValueError("Не удалось получить данные страны.")

        text = (
            f"<b>№ матча:</b> {number_match}\n"
            f"<b>Ваше государство:</b> {data_country['name_country']}\n\n"
            "<b>Ваш «Капитал»</b>\n"
        )

        text += "\n".join(
            f"{entry['amount']:,} {entry['currency_name']} ({entry['currency_tick']})"
            for entry in data_currency_capitals_from_country
        )

        text += '\n\n<b>Введите название валюты, которую хотите перевести:</b>'

        name_chart = await create_chart_currency_capitals_from_country(
            number_match=number_match,
            from_name_country=data_country['name_country'],
            data_currency_capitals=data_currency_capitals_from_country
        )



        chart_path = name_chart
        photo_chart = FSInputFile(chart_path)

        message = await message.answer_photo(
            photo=photo_chart,
            caption=text,
            parse_mode='html'
        )

        await update_state(state, message_id_delete=message.message_id)

        await state.set_state(SG.FormBankTransferRequest.currency_id)

    except (ValueError, Exception) as error:
        await callback_utils.handle_exception(message, 'input_name_currency_for_bank_transfer', error, '❌ <b>Ошибка на этапе выбора бенефициара.</b>')


@router.message(SG.FormBankTransferRequest.currency_id)
async def input_amount_currency_for_bank_transfer(message: Message, state: FSMContext):
    """
    Проверка ввода названия валюты и ввод объема, который планируйте отправить.
    """
    # try:
    #     await message.message.delete()
    # except Exception as error:
    #     await callback_utils.handle_error(message, error, f"Не удалось удалить сообщение")

    try:
        input_search_currency_name = message.text.strip()
        input_search_currency_name = str(input_search_currency_name).lower()

        form_choice_country = await state.get_data()
        number_match = form_choice_country['number_match']
        message_id_delete = form_choice_country['message_id_delete']


        data_currency_capitals_from_country = await DatabaseManager(
            database_path=number_match).get_data_currency_capitals_from_country(
            user_id=message.from_user.id,
            number_match=number_match
        )

        if not data_currency_capitals_from_country:
            raise ValueError("Не удалось получить капитал страны.")

        current_data_currency = {}

        for currency_capital in data_currency_capitals_from_country:
            if str(currency_capital['currency_name']).lower() == str(input_search_currency_name):
                current_data_currency = currency_capital

        if not current_data_currency:
            raise ValueError("Введенное названия не найдено в списке валют вашего капитала.\n\n<b>Повторите свой ввод еще раз.</b>")

        await delete_message(
            bot=message.bot,
            message_chat_id=message.chat.id,
            send_message_id=message_id_delete
        )

        await update_state(state, currency_id=current_data_currency['currency_id'])

        data_country = await DatabaseManager(database_path=number_match).get_data_country(
            user_id=message.from_user.id,
            number_match=number_match
        )

        if not data_country:
            raise ValueError("Не удалось получить данные страны.")


        message = await message.answer(callback=message,
             text=f'<b>№ матча:</b> {number_match}\n'
             f'<b>Ваше государство:</b> {data_country['name_country']}\n\n'
             f'<b>Вы располагаете:</b> {current_data_currency['amount']:,} {current_data_currency['currency_name']} ({current_data_currency['currency_tick']})\n\n'
             '<b>Укажите желаемый объем перевода:</b>',
             parse_mode='html'
        )

        await update_state(state, message_id_delete=message.message_id)

        await state.set_state(SG.FormBankTransferRequest.amount_currency_transfer)


    except (ValueError, Exception) as error:
        await callback_utils.handle_exception(message, 'input_amount_currency_for_bank_transfer', error, '❌ <b>Ошибка на этапе выбора валюты из капитала.</b>')


@router.message(SG.FormBankTransferRequest.amount_currency_transfer)
async def input_comment_for_bank_transfer(message: Message, state: FSMContext):
    """
    Проверка введенного объема валюты, и ввод комментария к банковской операции.
    """
    try:
        data_bank_transfer_request = await state.get_data()
        number_match = data_bank_transfer_request['number_match']
        currency_id = data_bank_transfer_request['currency_id']
        message_id_delete = data_bank_transfer_request['message_id_delete']

        data_currency_capitals_from_country = await DatabaseManager(
            database_path=number_match).get_data_currency_capitals_from_country(
            user_id=message.from_user.id,
            number_match=number_match
        )

        if not data_currency_capitals_from_country:
            raise ValueError("Не удалось получить капитал страны.")

        current_data_currency = {}

        for currency_capital in data_currency_capitals_from_country:
            if currency_capital['currency_id'] == int(currency_id):
                current_data_currency = currency_capital

        input_amount_currency = message.text.strip()
        amount_currency = float(input_amount_currency)

        if amount_currency <= 0:
            raise Exception('Объем перевода не может быть меньше или равно 0')
        elif amount_currency > current_data_currency['amount']:
            raise Exception('Вы не располагаете таким объемом валюты')

        await delete_message(
            bot=message.bot,
            message_chat_id=message.chat.id,
            send_message_id=message_id_delete
        )


        await update_state(state, amount_currency_transfer=amount_currency)

        await state.set_state(SG.FormBankTransferRequest.comment)

        data_country = await DatabaseManager(database_path=number_match).get_data_country(
            user_id=message.from_user.id,
            number_match=number_match
        )

        if not data_country:
            raise ValueError("Не удалось получить данные страны.")

        await message.answer(callback=message,
            text=f'<b>№ матча:</b> {number_match}\n'
            f'<b>Ваше государство:</b> {data_country['name_country']}\n\n'
            f'<b>Вы указали:</b> {amount_currency:,} {current_data_currency['currency_name']} ({current_data_currency['currency_tick']})\n\n'
            '<b>Укажите комментарий к вашему переводу:</b>',
            parse_mode='html'
        )

        await update_state(state, message_id_delete=message.message_id)
    except (ValueError, Exception) as error:
        await callback_utils.handle_exception(message, 'input_comment_for_bank_transfer', error, '❌ <b>Ошибка на этапе выбора объема перевода.</b>')


@router.message(SG.FormBankTransferRequest.comment)
async def end_bank_transfer(message: Message, state: FSMContext):
    """
    Проверка введенного тикера валюты и выбор ресурса за которым будет закреплена валюта
    """
    try:
        input_comment = message.text.strip().lower()
        if (len(input_comment) < 10) or (len(input_comment) > 70):
            raise Exception(
                "\nКомментарий должен содержать не менее 10 и не более 70 символов.\n\n"
                "<b>Вот примеры комментариев длиной 70 символов:</b>"
                "<blockquote>"
                    "1. 2000 зерна, цена 5000. Сумма сделки: 10 млн долларов.\n"
                    "2. Покупка Смоленска за 50 млн франков.\n"
                    "3. Вклад на сумму 140 млн марок.\n"
                    "4. Тестовый перевод."
                "</blockquote>"
            )

        await update_state(state, comment=input_comment)

        timezone = pytz.timezone("Europe/Moscow")
        now_date = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")

        await update_state(state, date_request_creation=now_date)

        await state.set_state(SG.FormBankTransferRequest.status_cancelled)

        await update_state(state, status_cancelled=False)

        await state.set_state(SG.FormBankTransferRequest.date_cancelled)

        await update_state(state, date_cancelled='')

        data_bank_transfer_request = await state.get_data()

        number_match = data_bank_transfer_request['number_match']
        payer_country_id = data_bank_transfer_request['payer_country_id']
        beneficiary_country_id = data_bank_transfer_request['beneficiary_country_id']
        currency_id = data_bank_transfer_request['currency_id']
        amount_currency_transfer = data_bank_transfer_request['amount_currency_transfer']
        comment = data_bank_transfer_request['comment']
        date_request_creation = data_bank_transfer_request['date_request_creation']
        message_id_delete = data_bank_transfer_request['message_id_delete']

        await delete_message(
            bot=message.bot,
            message_chat_id=message.chat.id,
            send_message_id=message_id_delete
        )

        payer_country_name = await DatabaseManager(database_path=number_match).get_country_name(country_id=payer_country_id)
        beneficiary_country_name = await DatabaseManager(database_path=number_match).get_country_name(country_id=beneficiary_country_id)
        currency_name = await DatabaseManager(database_path=number_match).get_currency_name(currency_id=currency_id)

        rough_draft_message = (
            f'<b>№ матча:</b> {number_match}\n'
            f'<b>Ваше государство:</b> {payer_country_name}\n'
            f'<b>Дата заявки:</b> {date_request_creation}\n\n'
            '<i>Проверьте правильно ли заполнены данные, по вашему переводу:</i>'
            '<blockquote>'
                f"<b>Матч:</b> {number_match}\n"
                f"<b>Отправитель:</b> {payer_country_name}\n"
                f"<b>Получатель:</b> {beneficiary_country_name}\n"
                f"<b>Название валюты:</b> {currency_name}\n"
                f"<b>Объем перевода:</b> {amount_currency_transfer}\n"
                f"<b>Комментарий:</b> {comment}\n"
            '</blockquote>'
        )

        keyboard = await launch_solution(
            launch_type='FormBankTransfer',
            number_match=number_match
        )

        sent_message = await message.answer(
            text=rough_draft_message,
            reply_markup=keyboard,
            parse_mode='html'
        )

        await update_state(state, message_id_delete=sent_message.message_id)
    except (ValueError, Exception) as error:
        await callback_utils.handle_exception(message, 'end_bank_transfer', error, '❌ <b>Ошибка на этапе комментария.</b>')


@router.callback_query(lambda c: c.data and c.data.startswith(f'{PREFIXES['CONFIRM']}_'))
async def confirm_form_bank_transfer(callback: CallbackQuery, state: FSMContext):
    """
    Подтверждение заполненной формы банковского перевода.
    """
    data_bank_transfer_request = await state.get_data()

    if not data_bank_transfer_request:

        await callback_utils.send_message(callback=callback,
            text='Возникла ошибка. Попробуйте повторить вашу банковскую операцию.'
        )

        number_match = callback_utils.parse_callback_data(callback.data, PREFIXES['CONFIRM'])[0]
        await start_bank_transfer(callback, state, number_match=number_match)

    elif data_bank_transfer_request:

        number_match = data_bank_transfer_request['number_match']
        payer_country_id = data_bank_transfer_request['payer_country_id']
        beneficiary_country_id = data_bank_transfer_request['beneficiary_country_id']
        currency_id = data_bank_transfer_request['currency_id']
        amount_currency_transfer = data_bank_transfer_request['amount_currency_transfer']
        comment = data_bank_transfer_request['comment']
        date_request_creation = data_bank_transfer_request['date_request_creation']
        status_cancelled = data_bank_transfer_request['status_cancelled']
        date_cancelled = data_bank_transfer_request['date_cancelled']
        message_id_delete = data_bank_transfer_request['message_id_delete']

        await delete_message(
            bot=callback.bot,
            message_chat_id=callback.message.chat.id,
            send_message_id=message_id_delete
        )

        await DatabaseManager(database_path=number_match).register_bank_transfer(
            number_match=number_match,
            payer_country_id=payer_country_id,
            beneficiary_country_id=beneficiary_country_id,
            currency_id=currency_id,
            amount_currency_transfer=amount_currency_transfer,
            comment=comment,
            date_request_creation=date_request_creation,
            status_cancelled=status_cancelled,
            date_cancelled=date_cancelled
        )

        await state.clear()

        data_bank_transfer_request = await DatabaseManager(database_path=number_match).get_bank_transfer(
            payer_country_id=payer_country_id,
            date_request_creation=date_request_creation
        )

        logger.info(f'data_bank_transfer_request from get_bank_transfer: {data_bank_transfer_request}')

        await DatabaseManager(database_path=number_match).execution_bank_transfer(
            data_bank_transfer_request=data_bank_transfer_request
        )

        payer_country_name = await DatabaseManager(database_path=number_match).get_country_name(country_id=data_bank_transfer_request['payer_country_id'])
        beneficiary_country_name = await DatabaseManager(database_path=number_match).get_country_name(country_id=data_bank_transfer_request['beneficiary_country_id'])
        currency_name = await DatabaseManager(database_path=number_match).get_currency_name(currency_id=data_bank_transfer_request['currency_id'])

        try:
            status_payer = await DatabaseManager(database_path=number_match).update_amount_national_currency_for_issuer(
                number_match=number_match,
                country_id=payer_country_id,
                currency_id=currency_id,
                currency_name=currency_name,
                amount_currency_transfer=amount_currency_transfer,
                payer=True
            )

            if not status_payer:
                status_beneficiary = await DatabaseManager(database_path=number_match).update_amount_national_currency_for_issuer(
                    number_match=number_match,
                    country_id=beneficiary_country_id,
                    currency_id=currency_id,
                    currency_name=currency_name,
                    amount_currency_transfer=amount_currency_transfer,
                    beneficiary=True
                )

                if not status_beneficiary:
                    logger.info('payer и beneficiary не являются эмитентами искомой валюты')
                elif status_beneficiary is None:
                    raise Exception('Данные beneficiary при подтверждении эмитента по банковскому переводу пусты!')
            elif status_payer is None:
                raise Exception('Данные payer при подтверждении эмитента по банковскому переводу пусты!')
        except Exception as error:
            logger.error(f'Ошибка в confirm_form_bank_transfer: {error}')

        finally_message_bank_transfer_for_payer = (
            f'<b>№ Банковского перевода: {data_bank_transfer_request['id']}</b>\n'
            f'<b>Статус:</b> Успешно✅\n\n'
            f'<b>№ матча:</b> {data_bank_transfer_request['number_match']}\n'
            f'<b>Ваше государство:</b> {payer_country_name}\n'
            f'<b>Дата заявки:</b> {data_bank_transfer_request['date_request_creation']}\n\n'
            '<blockquote>'
                f"<b>Матч:</b> {data_bank_transfer_request['number_match']}\n"
                f"<b>Отправитель:</b> {payer_country_name}\n"
                f"<b>Получатель:</b> {beneficiary_country_name}\n"
                f"<b>Название валюты:</b> {currency_name}\n"
                f"<b>Объем перевода:</b> {format_number(data_bank_transfer_request['amount_currency_transfer'])}\n"
                f"<b>Комментарий:</b> {data_bank_transfer_request['comment']}\n"
            '</blockquote>'
        )

        await callback_utils.send_message(callback=callback,
            text=finally_message_bank_transfer_for_payer,
        )

        beneficiary_message = (
            f'<b>Банковский перевод:</b>\n'
            f'<blockquote>'
                f'<b>№ матча:</b> {data_bank_transfer_request['number_match']}\n'
                f'<b>Ваше государство:</b> {beneficiary_country_name}\n'
                f'<b>Дата заявки:</b> {data_bank_transfer_request['date_request_creation']}\n\n'
                f'<b>Вам насчет поступило:</b> {format_number(data_bank_transfer_request['amount_currency_transfer'])} {currency_name}\n\n'
                f'<b>Отправитель:</b> {payer_country_name}\n'
                f'<b>Комментарий:</b> {data_bank_transfer_request['comment']}'
            f'</blockquote>'
        )

        beneficiary_country_telegram_id = await DatabaseManager(database_path=number_match).get_country_telegram_id(country_id=beneficiary_country_id)

        await callback.bot.send_message(
            chat_id=beneficiary_country_telegram_id,
            text=beneficiary_message,
            parse_mode="html"
        )


@router.callback_query(lambda c: c.data and c.data.startswith(f'{PREFIXES["RESTART"]}_'))
async def restart_form_bank_transfer(callback: CallbackQuery, state: FSMContext):
    """
    Перезапуск процесса заполнения формы банковского перевода.
    """
    try:
        number_match = callback_utils.parse_callback_data(callback.data, PREFIXES["RESTART"])[0]
        await state.clear()
        await start_bank_transfer(callback, state, number_match)
    except Exception as error:
        await callback_utils.handle_exception(callback, 'restart_form_emission_national_currency', error, '❌ <b>Не удалось перезапустить форму.</b>')
