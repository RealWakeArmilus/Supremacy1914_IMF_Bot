from aiogram import Bot

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
