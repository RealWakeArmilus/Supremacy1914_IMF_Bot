from asyncio.log import logger

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

# Импортируйте модули, которые используются внутри функций
import app.DatabaseWork.master as master_db
import app.keyboards as kb

from aiogram import Router

from app.message_designer.deletezer import delete_message_photo
from app.message_designer.randomaizer import generate_custom_random_unique_word

router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith('ChoiceMatchForUser_'))
async def start_choice_number_match_for_game_user(callback: CallbackQuery, state: FSMContext):
    """
    choice number match for game user

    :param state:
    :param callback:
    :return:
    """
    number_match = callback.data.split('_')[1]

    await callback.answer(
        f"Вы выбрали матч с номером: {number_match}")

    await delete_message_photo(callback, state)

    if await master_db.check_choice_state_in_match_db(number_match, callback.from_user.id):

        await callback.message.answer(
            'Вы уже выбрали в данном матче государство. Но ваша заявка еще на проверке.'
            '<pre>Для подтверждения вашей заявки требуется написать кодовое слово IMF в самой игре supremacy1914, через то государство которое выбрали в боте</pre>',
            parse_mode="html")

    else:

        await callback.message.answer(
            f'Выберите государство за которое играете, на карте: {number_match}.'
            '<pre>Нужно указать только то государство, которым вы реально управляете в игре Supremacy1914.</pre>',
            reply_markup=await kb.free_states_match(f'ChoiceStateFromMatch_{number_match}', number_match),
            parse_mode="html")


@router.callback_query(lambda c: c.data and c.data.startswith('ChoiceStateFromMatch_'))
async def choice_state_from_number_match_for_user(callback: CallbackQuery):
    try:
        number_match = callback.data.split('_')[1]
        name_state = callback.data.split('_')[2]

        await callback.answer(f"Вы выбрали государство: {name_state}")

        await callback.message.edit_text('Обработка...')

        unique_word = generate_custom_random_unique_word()

        await callback.message.edit_text(
            'Следуйте инструкции подтверждения вашей заявки:'
            f'<pre>'
            f'1. Заходите в игру Supremacy1914;\n'
            f'2. Заходите в матч под номером: {number_match};\n'
            f'3. Находите игрока с ником "Company Mekas", он же "International Monetary Fund";\n'
            f'4. Пишите ему кодовое слово: {unique_word};\n'
            f'5. Ждете подтверждение вашей заявки.\n'
            f'</pre>'
            f'\n<pre>'
            f'Важно: кодовое слово никому не передавать.\n'
            f'Если кто-то захочет играть за вас, он будет требовать от вас кодовое слово.\n'
            f'Если он подал заявку на ваше государство до вас, то без вашего письма в игре он не сможет подтвердить свою подлинность.\n'
            f'</pre>',
            parse_mode="html"
        )

        chat_id_admin = await master_db.get_telegram_id_admin()

        await callback.bot.send_message(chat_id=chat_id_admin,
                                        text='<b>Заявка на подтверждение выбора государства</b>'
                                        f'\n<b>Матч:</b> {number_match}'
                                        f'\n<b>Государство:</b> {name_state}'
                                        f'\n<b>Кодовое слово:</b> {unique_word}',
                                        parse_mode="html")
    except Exception as error:
        # Логирование ошибки
        logger.error(f"Ошибка в функции choice_state_from_number_match_for_user: {error}")
        await callback.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже.")
        await callback.message.edit_text('Произошла ошибка при обработке вашего запроса.')
