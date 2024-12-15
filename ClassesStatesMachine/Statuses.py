import enum


class TypeChat(enum.Enum):
    """
    :var USER: user
    :var GROUP: group
    :var SUPERGROUP: supergroup
    :var CHANNEL: channel
    :var UNKNOWN: unknown
    """

    USER : str = 'user'
    GROUP : str = 'group'
    SUPERGROUP : str = 'supergroup'
    CHANNEL : str = 'channel'
    UNKNOWN : str = 'unknown'


class TypeUser(enum.Enum):
    """
    :var ADMIN: admin
    :var MODERATOR: moderator
    :var SIMPLE: simple
    """
    ADMIN : str = 'admin'
    MODERATOR : str = 'moderator'
    SIMPLE : str = 'simple'


class VerifyStatus(enum.Enum):

    USER_OWNER_BOT : int = 1000
    USER_NO_REGISTRATION_IN_DATA_BASE : int = 1001
    USER_REGISTRATION_IN_DATA_BASE : int = 1002
    USER_BAN_IN_DATA_BASE : int = 1003
    UNKNOWN_CHAT_OF_ADDRESSER : int = 3000


"""
Результаты проверки tg_id

Для пользователей:
    VerifyStatus.USER_OWNER_BOT = 1000 : пользователей владелец бота
    VerifyStatus.USER_NO_REGISTRATION_IN_DATA_BASE = 1001 : пользователь не зарегистрирован, в системе бота
    VerifyStatus.USER_REGISTRATION_IN_DATA_BASE = 1002 : пользователь зарегистрирован, в системе бота
    VerifyStatus.USER_BAN_IN_DATA_BASE = 1003 : пользователь попал в "черный-список" системы бота

Неизвестен чат обращающего:
    VerifyStatus.UNKNOWN_CHAT_OF_ADDRESSER = 3000 : неизвестный чат адресанта

"""
