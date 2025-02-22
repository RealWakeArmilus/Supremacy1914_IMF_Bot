from tortoise import Tortoise, fields
from tortoise.models import Model
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# ---------------------
# Инициализация ORM
# ---------------------
async def init_db(db_url: str):
    await Tortoise.init(
        db_url=f'sqlite://database/{db_url}.db',  # Подключение к SQLite
        modules={'models': ['app.DatabaseWork.tortoise_orm']}  # Автоимпорт моделей
    )
    await Tortoise.generate_schemas()


async def close_db():
    await Tortoise.close_connections()


# ---------------------
# Определение моделей
# ---------------------
class User(Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.IntField(unique=True)
    username = fields.CharField(max_length=50, null=True)
    is_admin = fields.BooleanField(default=False)


class Match(Model):
    id = fields.IntField(pk=True)
    number_match = fields.IntField(unique=True)
    type_map = fields.CharField(max_length=50)


class Countries(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    telegram_id = fields.IntField(default=0)
    admin = fields.BooleanField(default=False)


class CountryChoiceRequests(Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.IntField()
    number_match = fields.IntField()
    name_country = fields.CharField(max_length=50)
    unique_word = fields.CharField(max_length=15, unique=True)
    admin_decision_message_id = fields.IntField()


class Currencies(Model):
    id = fields.IntField(pk=True)
    country = fields.ForeignKeyField('models.Countries', related_name='Country')
    name = fields.CharField(max_length=50)
    tick = fields.CharField(max_length=10, unique=True)
    following_resource = fields.CharField(max_length=50)
    course_following = fields.FloatField()
    capitalization = fields.IntField()
    emission = fields.FloatField()
    current_amount = fields.FloatField()
    current_course = fields.FloatField()


class CurrencyEmissionRequests(Model):
    id = fields.IntField(pk=True)
    number_match = fields.IntField()
    telegram_id = fields.IntField()
    country_id = fields.ForeignKeyField('models.Countries', related_name='currency_emission_requests')
    name_currency = fields.CharField(max_length=50)
    tick_currency = fields.CharField(max_length=10)
    following_resource = fields.CharField(max_length=50)
    course_following = fields.FloatField()
    capitalization = fields.IntField()
    amount_emission_currency = fields.FloatField()
    date_request_creation = fields.DatetimeField(auto_now_add=True)
    status_confirmed = fields.BooleanField(default=False)
    date_confirmed = fields.DatetimeField(null=True)
    message_id_delete = fields.IntField(null=True)


class BankTransferRequests(Model):
    id = fields.IntField(pk=True)
    number_match = fields.IntField()
    payer_country_id = fields.ForeignKeyField('models.Countries', related_name='payer_transfers')
    beneficiary_country_id = fields.ForeignKeyField('models.Countries', related_name='beneficiary_transfers')
    currency_id = fields.ForeignKeyField('models.Currencies', related_name='transfers')
    amount_currency_transfer = fields.FloatField()
    comment = fields.TextField(null=True)
    date_request_creation = fields.DatetimeField(auto_now_add=True)
    status_cancelled = fields.BooleanField(default=False)
    date_cancelled = fields.DatetimeField(null=True)


class DatabaseManager:
    async def create(self, model, **fields):
        """ Создает новую запись в таблице."""
        try:
            obj = await model.create(**fields)
            return obj
        except Exception as e:
            logger.error(f'Ошибка при создании {model.__name__}: {e}')
            return None

    async def insert(self, model, data: List[Dict[str, Any]]):
        """ Вставка одной или нескольких записей."""
        try:
            if not data:
                raise ValueError("Данные для вставки пустые")
            await model.bulk_create([model(**item) for item in data])
        except Exception as e:
            logger.error(f'Ошибка при вставке данных в {model.__name__}: {e}')

    async def fetch_records(self, model, filters: Optional[Dict[str, Any]] = None, single: bool = False) \
    -> Optional[List[Dict[str, Any]]]:
        """ Получение записей из базы.

        :param model: ORM-модель (таблица)
        :param filters: Словарь фильтров для поиска (опционально)
        :param single: Если True - вернет одну запись, иначе список записей
        """
        query = model.all()
        if filters:
            query = query.filter(**filters)
        records = await query.values()

        if single:
            return records[0] if records else None
        return records if records else []

    async def delete(self, model, filters: Dict[str, Any]) \
    -> int:
        """Удаляет записи, возвращает количество удаленных строк."""
        return await model.filter(**filters).delete()

    async def update(self, model, filters: Dict[str, Any], data_set: Dict[str, Any]) \
    -> int:
        """Обновляет записи, возвращает количество обновленных строк."""
        return await model.filter(**filters).update(**data_set)

    async def get_all_match_numbers(self) \
    -> List[int]:
        """ Получение всех номеров матчей."""
        matches = await Match.all().values_list('number', flat=True)
        return list(matches)

    async def set_match(self, number_match: int, type_match: str):
        """ Добавление нового матча."""
        await self.create(Match, number=number_match, type_map=type_match)

    async def get_currency_by_country(self, country_id: int) \
    -> List[Dict[str, Any]]:
        """ Получение списка валют страны."""
        currencies = await Currencies.filter(country_id=country_id).values()
        return currencies

    async def update_course_alone_currency(self, currency_id: int, emission: float, current_amount: float, course_following: float):
        """ Обновление курса конкретной валюты."""
        if current_amount <= 0:
            new_course = 1
        elif emission <= 0 or course_following <= 0:
            new_course = 1
        else:
            new_course = (current_amount / emission) * course_following
            new_course = round(1 / new_course, 9)

        await self.update(Currencies, {'id': currency_id}, {'current_course': new_course})


class UserManager(DatabaseManager):
    async def add_user(self, telegram_id: int, username: str):
        """Добавляет нового пользователя в базу."""
        existing_user = await self.fetch_records(User, filters={"telegram_id": telegram_id}, single=True)
        if existing_user:
            return existing_user
        return await self.create(User, telegram_id=telegram_id, username=username)

    async def get_user(self, telegram_id: int) \
    -> list[dict[str, Any]]:
        """Получает данные пользователя."""
        return await self.fetch_records(User, filters={"telegram_id": telegram_id}, single=True)

    async def set_admin(self, telegram_id: int):
        """Назначает пользователя админом."""
        await self.update(User, filters={"telegram_id": telegram_id}, data_set={"is_admin": True})

    async def get_admins(self) \
    -> List[Dict[str, Any]]:
        """Получает список администраторов."""
        return await self.fetch_records(User, filters={"is_admin": True})


class MatchesManager(DatabaseManager):
    async def create_match(self, number_match: int, type_map: str):
        """Добавляет новый матч."""
        if number_match is None or type_map is None:
            logger.error(f'Ошибка: number_match={number_match}, type_match={type_map} - Неверные данные!')
            return None

        match, created = await Match.get_or_create(
            number_match=number_match,
            defaults={"type_map": type_map}
        )

        if not created:
            logger.warning(f'Матч {number_match} уже существует!')

        if match is None:
            logger.error(f'Ошибка: матч {number_match} не создан в базе!')
        return match

    async def get_all_matches(self) \
    -> List[Dict[str, Any]]:
        """Возвращает список всех матчей."""
        return await self.fetch_records(Match)

    async def match_exists(self, number_match: int) \
    -> bool:
        """Проверяет, существует ли матч."""
        match = await self.fetch_records(Match, filters={"number": number_match}, single=True)
        return match is not None

    async def delete_match(self, number_match: int):
        """Удаляет матч."""
        await self.delete(Match, {"number": number_match})

    async def initialize_match(self, number_match: int):
        """Создает новую базу данных для матча и инициализирует таблицы."""
        await init_db(db_url=str(number_match))

        countries = [
            {'name': '', 'telegram_id': 0, 'admin': False},
            {'name': '', 'telegram_id': 0, 'admin': False}
        ]
        await self.insert(Countries, countries)

        currencies = [
            {'name': '', 'tick': '', 'country_id': 0, 'following_resource': '',
             'course_following': 0, 'capitalization': 0, 'emission': 0, 'current_amount': 0,
             'current_course': 0}
        ]
        await self.insert(Currencies, currencies)

        await close_db()


class CurrencyManager(DatabaseManager):
    async def add_currency(self, country_id: int, name: str, tick: str, following_resource: str,
                           course_following: float, capitalization: int, emission: float):
        """Добавляет новую валюту."""
        return await self.create(
            Currencies,
            country_id=country_id, name=name, tick=tick,
            following_resource=following_resource, course_following=course_following,
            capitalization=capitalization, emission=emission,
            current_amount=emission, current_course=0.0
        )

    async def get_currencies_by_country(self, country_id: int) \
    -> List[Dict[str, Any]]:
        """Возвращает все валюты страны."""
        return await self.fetch_records(Currencies, filters={"country_id": country_id})

    async def update_currency_course(self, currency_id: int, emission: float, current_amount: float, course_following: float):
        """Обновляет курс валюты."""
        new_course = 1 if current_amount <= 0 else round(1 / ((current_amount / emission) * course_following), 9)
        await self.update(Currencies, {"id": currency_id}, {"current_course": new_course})

    async def delete_currency(self, currency_id: int):
        """Удаляет валюту."""
        await self.delete(Currencies, {"id": currency_id})



