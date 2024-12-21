import app.verify.checks as checks
import ClassesStatesMachine.Statuses as Status


async def verify(type_chat : str, chat_id : int, user_id : int):
    """

    :param type_chat: message.chat.type
    :param chat_id: message.chat.id
    :param user_id: message.from_user.id
    :return:
    """
    status_type_chat = await checks.identify_chat_type(type_chat)

    if status_type_chat == Status.TypeChat.USER:

        return await checks.identify_user_admin(chat_id)

    else:

        pass
