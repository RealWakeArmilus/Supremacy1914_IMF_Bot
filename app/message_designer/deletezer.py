from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery


async def delete_message(message, message_chat_id, send_message_message_id):
    """
    deletes a specific message by message ID, provided that it is in one function and not in a callback

    :param message: message.bot
    :param message_chat_id: message.chat.id
    :param send_message_message_id: send_message.message_id
    :return:
    """
    await message.delete_message(
        chat_id=message_chat_id,
        message_id=send_message_message_id)


async def delete_message_photo(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    photo_message_id = data.get('photo_message_id')

    if photo_message_id:
        try:
            # Удаление сообщения с фотографией
            await callback.message.chat.delete_message(photo_message_id)
        except Exception as error:
            # Обработка возможных ошибок, например, если сообщение уже удалено
            print(f"Ошибка при удалении сообщения: {error}")
