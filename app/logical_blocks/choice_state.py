from asyncio.log import logger

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

# Импортируйте модули, которые используются внутри функций
import app.DatabaseWork.master as master_db
import app.DatabaseWork.match as match_db

# import keyboards
import app.keyboards.choice_state as kb

from aiogram import Router

from app.message_designer.deletezer import delete_message_photo
from app.message_designer.randomaizer import generate_custom_random_unique_word

router = Router()


# import routers from logical_blocks
from app.logical_blocks.verify_state import router as verify_state_router
from app.logical_blocks.country_menu import router as country_menu_router

# connect routers from logical_blocks
router.include_router(verify_state_router)
router.include_router(country_menu_router)

from app.logical_blocks.country_menu import start_country_menu



@router.callback_query(lambda c: c.data and c.data.startswith('ChoiceMatchForUser_'))
async def start_choice_number_match_for_game_user(callback: CallbackQuery, state: FSMContext):
    """
    choice number match for game user

    :param state:
    :param callback:
    :return:
    """
    number_match = callback.data.split('_')[1]

    await callback.answer(f"Вы выбрали матч с номером: {number_match}")

    await delete_message_photo(callback, state)


    request_state = await match_db.check_request_choice_state(number_match, callback.from_user.id)

    if request_state is False:

        data_state = await match_db.check_choice_state_in_match_db(number_match, callback.from_user.id)

        if data_state:

            await callback.message.answer(f'<b>Вы играете за:</b> {data_state['name_state']}',
                                          parse_mode="html")

            # Вызываем функцию start_created_match
            await start_country_menu(callback)

        elif data_state is None:

            await callback.message.answer(f'Выберите государство за которое играете, на карте: {number_match}.'
                                          '<pre>Нужно указать только то государство, которым вы реально управляете в игре Supremacy1914.</pre>',
                                          reply_markup=await kb.free_states_match(f'ChoiceStateFromMatch_{number_match}', number_match),
                                          parse_mode="html")

        else:

            await callback.message.answer('Что-то пошло не так "logical_blocks/choice_state/65"')

    elif request_state:

        await callback.message.answer('По всей видимости ваша заявка была отклонена. '
                                      '\nПопробуйте еще раз. Следуйте инструкции.',
                                      reply_markup=await kb.free_states_match(f'ChoiceStateFromMatch_{number_match}', number_match),
                                      parse_mode="html")

    else:

        await callback.message.answer('Что-то пошло не так "logical_blocks/choice_state/76"')




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

        admin_decision_message_id = await callback.bot.send_message(chat_id=chat_id_admin,
                                        text='<b>Заявка на подтверждение выбора государства</b>'
                                        f'\n<b>Матч:</b> {number_match}'
                                        f'\n<b>Государство:</b> {name_state}'
                                        f'\n<b>Кодовое слово:</b> {unique_word}',
                                        reply_markup=await kb.state_verify_by_admin(unique_word, number_match),
                                        parse_mode="html")

        # save chat_id user and data request choice state
        await match_db.save_request_choice_state(callback.from_user.id, number_match, name_state, unique_word, admin_decision_message_id.message_id)

    except Exception as error:
        logger.error(f"Ошибка в функции choice_state_from_number_match_for_user: {error}")
        await callback.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже.")
        await callback.message.edit_text('Произошла ошибка при обработке вашего запроса.')

