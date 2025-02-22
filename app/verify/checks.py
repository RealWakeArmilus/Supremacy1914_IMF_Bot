from SPyderSQL import SQLite
from app.config import CHANNEL_USERNAME
import ClassesStatesMachine.Statuses as Status
import logging

logger = logging.getLogger(__name__)


async def identify_subscription(bot, user_id: int) -> bool:
    """--- Проверка подписки ---"""
    try:
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logging.error(f"Ошибка при проверке подписки: {e}")
        return False

async def identify_chat_type(chat_type : str) -> Status.TypeChat:
    """
    Checks type user.
    \nПроверяет тип пользователя.

    :param chat_type: message.chat.type
    :return: status chat type
    """
    if chat_type == "private":

        return Status.TypeChat.USER

    elif chat_type == "group":

        return Status.TypeChat.GROUP

    elif chat_type == "supergroup":

        return Status.TypeChat.SUPERGROUP

    elif chat_type == "channel":

        return Status.TypeChat.CHANNEL

    else:

        return Status.TypeChat.UNKNOWN


async def identify_user_admin(chat_id: int) -> Status.TypeUser:
    """

    :param chat_id: message.chat.id
    :return: status user type
    """
    data_users = SQLite.select_table('database/master.db',
                                 'users',
                                 ['telegram_id', 'admin'])

    for user in data_users:

        if chat_id == user['telegram_id']:

            if user['admin']:

                return Status.TypeUser.ADMIN

    return Status.TypeUser.SIMPLE
