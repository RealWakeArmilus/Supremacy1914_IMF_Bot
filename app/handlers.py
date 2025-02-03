from aiogram import Router
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile

# import keyboards
import app.keyboards.handlers as kb_handlers
import app.keyboards.settings_match as kb_settings_match

# import verify
import app.verify.checks as checks
import app.verify.admin as admin

# import ClassState
import ClassesStatesMachine.SG as SG
from app.DatabaseWork.database import DatabaseManager


# Для передачи сигнала в данный файл, что запуск команд идет здесь
router = Router()

# import routers from logical_blocks
from app.logical_blocks.created_match import router as created_match_router
from app.logical_blocks.settings_match import router as settings_match_router
from app.logical_blocks.choice_country import router as choice_state_router

# connect routers from logical_blocks
router.include_router(created_match_router)
router.include_router(settings_match_router)
router.include_router(choice_state_router)


@router.message(Command('initialize_bot1243'))
async def cmd_admin(message: Message):

    try:
        await DatabaseManager().initialize_master()
    except Exception as error:
        await message.answer(text=f'Инициализация бота прошла с ошибкой: {error}')

    await message.answer(text='Инициализация бота прошла успешно!')


@router.message(Command('admin'))
async def cmd_admin(message: Message):

    status_type_user = await admin.verify(message.chat.type, message.chat.id, message.from_user.id)

    if status_type_user == admin.Status.TypeUser.ADMIN:

        await message.answer(
            f'<b>Здравствуйте администратор:</b> {message.from_user.full_name}.\n'
            f'<b>Версия бота:</b> 0.1.3.4 (tick48)',
            reply_markup=kb_handlers.admin_menu,
            parse_mode='html')

    elif status_type_user == admin.Status.TypeUser.SIMPLE:

        await message.answer('Вы не являетесь администратором.')

    else:

        pass


@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):

    status_type_chat = await checks.identify_chat_type(message.chat.type)

    if status_type_chat == checks.Status.TypeChat.USER:

        if await kb_settings_match.numbers_match():

            photo_path = 'image/exemple_number_match.jpg'
            photo = FSInputFile(photo_path)

            await message.answer(
                text='Здравствуйте! Создатель этого бота: <a href="https://t.me/L_e_m_b_e_r_g_w_a_k_e">_L_e_m_</a>',
                parse_mode='html'
            )

            sent_message = await message.answer_photo(
                photo,
                'Выберите <b>Номер матча</b> из списка ниже.'
                '\n<pre>Узнать номер матча можно в игре supremacy1914, как указано на скрине.</pre>',
                reply_markup=await kb_settings_match.numbers_match('ChoiceMatchForUser'),
                parse_mode='html')

            # Сохранение message_id фотографии в состоянии пользователя
            await state.set_state(SG.SavePhotoMessageID.photo_message_id.state)
            await state.update_data(photo_message_id=sent_message.message_id)

        else:

            await message.answer(
                'Здравствуйте!'
                '\nНа текущий момент игровых сессий не существует.'
                '\nНапишите <a href="https://t.me/L_e_m_b_e_r_g_w_a_k_e">администратору</a> чтобы он её создал.',
                parse_mode='html')

    else:

        pass


@router.message(Command('send_video'))
async def cmd_start(message: Message):

    video_path = 'image/video_test.mp4'
    video = FSInputFile(video_path)

    await message.answer_video(
        video=video,
        caption='Описание под видео'
    )
