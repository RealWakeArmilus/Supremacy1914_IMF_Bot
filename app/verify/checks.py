from SPyderSQL import SQLite
import ClassesStatesMachine.Statuses as Status


import app.DatabaseWork.master as master_db


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
    await master_db.created_table_user()

    data_users = SQLite.select_table('database/master.db',
                                 'users',
                                 ['telegram_id', 'admin'])

    for user in data_users:

        if chat_id == user['telegram_id']:

            if user['admin']:

                return Status.TypeUser.ADMIN

    return Status.TypeUser.SIMPLE
