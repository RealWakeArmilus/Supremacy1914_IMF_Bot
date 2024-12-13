from SPyderSQL import SQLite
import ClassesStatesMachine.Statuses as Status


# Запуск верификации чата, который обращается к боту
def start_verification(type_chat : str, chat_id : int, user_id : int) -> Status.VerifyStatus:

    if is_user(type_chat):

        return for_user(user_id)

    else:

        return Status.VerifyStatus.UNKNOWN_CHAT_OF_ADDRESSER


# чат является пользователем?
def is_user(type_chat : str) -> bool:
    """
    :param type_chat: message.chat.type
    :return: bool значение, означающий является ли данный tg_id чатом пользователя или нет
    """

    # Пользователь обратился к боту напрямую
    if type_chat == 'private':

        return True

    # Пользователь обратился к боту не напрямую
    else:

        return False


# процесс для пользователя, обратившегося к боту напрямую
def for_user(user_tg_id : int) -> Status.VerifyStatus:

    info_chat = exists(user_tg_id, 0)

    # Проверка пользователя на регистрацию в системе бота
    # Если пользователь зарегистрирован в системе бота
    if info_chat:

        print('Проверяем {tg_id} в БД «Users» на статус Owner'.format(tg_id=user_tg_id))

        # Проверка пользователя на статус владельца ботом
        # Пользователь является владельцем бота
        if info_chat['owner']:

            return Status.VerifyStatus.USER_OWNER_BOT

        # Пользователь не является владельцем бота
        elif not info_chat['owner']:

            print('Проверяем {tg_id} в БД «Users» на статус Ban'.format(tg_id=user_tg_id))

            # Проверка пользователя на нахождении в "Черном-списке" бота
            # Пользователь попал в "Черный-список" бота
            if info_chat['ban']:

                return Status.VerifyStatus.USER_BAN_IN_DATA_BASE

            # Пользователь не в "Черном-списке" бота
            elif not info_chat['ban']:

                return Status.VerifyStatus.USER_REGISTRATION_IN_DATA_BASE

    # Если пользователь не зарегистрирован в системе бота
    elif not info_chat:

        return Status.VerifyStatus.USER_NO_REGISTRATION_IN_DATA_BASE


# Проверяем чат на регистрацию в БД
def exists(search_tg_id : int, type_tg_id : int) -> dict:
    """
    :param search_tg_id: уникальный id группы message.chat.id, или id чата пользователя message.from_user.id
    :param type_tg_id: указываем тип на который мы хотим проверить tg_id, где 0 - Users, 1 - Groups
    :return: bool значение, означающий существование tg_id в БД бота
    """

    if type_tg_id == 0:

        print('Проверяем {tg_id} в БД «Users», на регистрацию'.format(tg_id=search_tg_id))

        user = find_user_by_tg_id(connect_table_users(), search_tg_id)

        # Пользователь не зарегистрирован в БД
        if not user:

            return user

        # Пользователь зарегистрирован в БД
        else:

            return user

    # elif type_tg_id == 1:
    #
    #     print('Проверяем {tg_id} в БД «Groups», на существование'.format(tg_id=search_tg_id))
        # return one_for(id_chats, 'tg_id', search_tg_id)

    else:

        print('Неизвестный type_tg_id')
