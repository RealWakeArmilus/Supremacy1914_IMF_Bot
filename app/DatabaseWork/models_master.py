from datetime import datetime
from tortoise import fields
from tortoise.models import Model
from app.DatabaseWork.control_db import DatabaseManager
from app.DatabaseWork.control_db import init_master_db, close_db
from tortoise.exceptions import IntegrityError, OperationalError
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


# ---------------------
# Определение моделей
# ---------------------
class User(Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.IntField(unique=True)
    username = fields.CharField(max_length=50, null=True)
    first_name = fields.CharField(max_length=50, null=True)
    last_name = fields.CharField(max_length=50, null=True)
    is_free = fields.BooleanField(default=True)
    is_premium = fields.BooleanField(default=False)
    is_partner = fields.BooleanField(default=False)
    is_admin = fields.BooleanField(default=False)
    is_organization_process = fields.BooleanField(default=False)
    is_owner = fields.BooleanField(default=False)
    start_premium = fields.DatetimeField(null=True)
    end_premium = fields.DatetimeField(null=True)
    count_premium = fields.IntField(unique=True)


class Match(Model):
    id = fields.IntField(pk=True)
    number_match = fields.IntField(unique=True)
    id_user_owner_match = fields.CharField(max_length=50, null=True)
    type_map = fields.CharField(max_length=50)


# ---------------------
# Менеджеры таблиц
# ---------------------
class UserManager(DatabaseManager):
    async def add_user(self, telegram_id: int, username: str):
        """Добавляет нового пользователя в базу."""
        try:
            await init_master_db()
            existing_user = await self.fetch_records(User, filters={"telegram_id": telegram_id}, single=True)
            if existing_user:
                return existing_user
            return await self.create(User, telegram_id=telegram_id, username=username)
        finally:
            await close_db()


    async def set_user(self, telegram_id: int, username: str, first_name: str, last_name: str, start_premium: datetime | None, end_premium: datetime | None, count_premium: int):
        """Создает запись нового пользователя"""
        try:
            await init_master_db()
            await self.insert(
                model=User,
                data=[{
                    "telegram_id": telegram_id,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                    'start_premium': start_premium if start_premium else datetime.min,
                    'end_premium': end_premium if end_premium else datetime.min,
                    'count_premium': count_premium
                }]
            )
        finally:
            await close_db()


    async def get_user(
            self,
            first_name: Optional[str] = None,
            last_name: Optional[str] = None,
            username: Optional[str] = None,
            telegram_id: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """
        Получает данные пользователя по введённым параметрам.

        :param first_name: Имя пользователя (опционально)
        :param last_name: Фамилия пользователя (опционально)
        :param username: Никнейм пользователя (опционально)
        :param telegram_id: Telegram ID пользователя (опционально)
        :return: Список словарей с данными пользователя
        """
        filters = {}

        if first_name:
            filters["first_name"] = first_name
        if last_name:
            filters["last_name"] = last_name
        if username:
            filters["username"] = username
        if telegram_id:
            filters["telegram_id"] = telegram_id

        if not filters:
            raise ValueError("Необходимо передать хотя бы один параметр для поиска!")

        try:
            await init_master_db()
            return await self.fetch_records(User, filters=filters, single=True)
        finally:
            await close_db()


    async def set_admin(self, telegram_id: int):
        """Назначает пользователя админом."""
        try:
            await init_master_db()
            await self.update(User, filters={"telegram_id": telegram_id}, data_set={"is_admin": True})
        finally:
            await close_db()


    async def get_admins(self) \
    -> List[Dict[str, Any]]:
        """Получает список администраторов."""
        try:
            await init_master_db()
            return await self.fetch_records(User, filters={"is_admin": True})
        finally:
            await close_db()


class MatchesManager(DatabaseManager):
    async def create_match(self, number_match: int, id_user_owner_match: str, type_map: str):
        """Добавляет новый матч."""
        if not all([number_match, id_user_owner_match, type_map]):
            logger.error(
                f'Ошибка: number_match={number_match}, id_user_owner_match={id_user_owner_match}, type_map={type_map} - Неверные данные!')
            return None

        await init_master_db()

        try:
            match, created = await Match.get_or_create(
                number_match=number_match,
                defaults={
                    "id_user_owner_match": id_user_owner_match,
                    "type_map": type_map
                }
            )

            if not created:
                logger.warning(f'Матч {number_match} уже существует!')

            return match
        except IntegrityError as e:
            logger.error(f'Ошибка целостности данных: {e}')
        except OperationalError as e:
            logger.error(f'Ошибка базы данных: {e}')
        except Exception as e:
            logger.error(f'Неизвестная ошибка: {e}')
        finally:
            await close_db()

        return None


    async def get_all_matches(self) \
    -> List[Dict[str, Any]]:
        """Возвращает список всех матчей."""
        try:
            await init_master_db()
            return await self.fetch_records(Match)
        finally:
            await close_db()


    async def match_exists(self, number_match: int) \
    -> bool:
        """Проверяет, существует ли матч."""
        try:
            await init_master_db()
            match = await self.fetch_records(Match, filters={"number_match": number_match}, single=True)
            return match is not None
        finally:
            await close_db()


    async def delete_match(self, number_match: int):
        """Удаляет матч."""
        try:
            await init_master_db()
            await self.delete(Match, {"number_match": number_match})
        finally:
            await close_db()




