import os
import sqlite3
from typing import List, Optional

from SPyderSQL import SQLite, TypesSQLite
import app.DatabaseWork.match as match_db

# Constants
MASTER_DB_PATH = 'database/master.db'


class DatabaseManager:
    """Базовый менеджер для работы с SQLite базой данных."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def create_table(self, table_name: str, columns: dict):
        """Создает таблицу в базе данных."""
        SQLite.create_table(
            self.db_path,
            table_name,
            columns,
            True
        )

    async def insert(self, table_name: str, columns: List[str], values: tuple):
        """Вставляет запись в таблицу."""
        SQLite.insert_table(
            self.db_path,
            table_name,
            columns,
            values
        )

    async def select(self, table_name: str, columns: List[str], where_clause: Optional[str] = None, params: Optional[tuple] = None):
        """Выбирает записи из таблицы."""
        return SQLite.select_table(
            self.db_path,
            table_name,
            columns,
            # where_clause,
            # params
        )

    async def delete(self, table_name: str, where_clause: str, params: tuple):
        """Удаляет записи из таблицы."""
        with sqlite3.connect(self.db_path) as db:
            db.execute(f"DELETE FROM {table_name} WHERE {where_clause}", params)
            db.commit()


class MasterDatabase(DatabaseManager):
    """Менеджер для мастер-базы данных."""

    def __init__(self, db_path: str = MASTER_DB_PATH):
        super().__init__(db_path)

    async def initialize(self):
        """Инициализирует необходимые таблицы в мастер-базе."""
        await self.create_table('match', {
            'number': TypesSQLite.integer.value,
            'type_map': TypesSQLite.text.value
        })

    async def add_match(self, number_match: int, type_match: str):
        """Добавляет новый матч в мастер-базу."""
        await self.insert(
            'match',
            ['number', 'type_map'],
            (number_match, type_match)
        )

    async def match_exists(self, number: int) -> bool:
        """Проверяет существование матча по номеру."""
        matches = await self.select('match', ['number'])
        return any(match['number'] == number for match in matches)

    async def get_all_match_numbers(self) -> List[int]:
        """Возвращает список всех номеров матчей."""
        matches = await self.select('match', ['number'])
        return [match['number'] for match in matches]

    async def delete_match_record(self, number_match: int) -> bool:
        """Удаляет запись матча из мастер-базы."""
        try:
            await self.delete('match', 'number = ?', (number_match,))
            return True
        except Exception as e:
            print(f"Ошибка при удалении матча {number_match}: {e}")
            return False

    async def initialize_users(self):
        """Инициализирует таблицу пользователей."""
        await self.create_table('users', {
            'telegram_id': TypesSQLite.integer.value,
            'admin': TypesSQLite.integer.value
        })

    async def add_admin(self, telegram_id: int):
        """Добавляет администратора в таблицу пользователей."""
        await self.insert(
            'users',
            ['telegram_id', 'admin'],
            (telegram_id, True)
        )

    async def get_admin_telegram_id(self) -> Optional[int]:
        """Возвращает telegram_id администратора."""
        users = await self.select('users', ['telegram_id', 'admin'])
        for user in users:
            if user['admin']:
                return user['telegram_id']
        return None


class MatchDatabase(DatabaseManager):
    """Менеджер для базы данных конкретного матча."""

    def __init__(self, number_match: int):
        db_path = f'database/{number_match}.db'
        super().__init__(db_path)
        self.number_match = number_match

    async def initialize(self, type_match: str):
        """Инициализирует все необходимые таблицы для матча."""

        await self.create_table('countries', {
            'name': TypesSQLite.text.value,
            'telegram_id': TypesSQLite.integer.value,
            'admin': TypesSQLite.blob.value
        })

        await self.create_table('country_choice_requests', {
            'telegram_id': TypesSQLite.integer.value,
            'number_match': TypesSQLite.integer.value,
            'name_country': TypesSQLite.text.value,
            'unique_word': TypesSQLite.text.value,
            'admin_decision_message_id': TypesSQLite.integer.value
        })

        await self.create_table('currency', {
            'country_id': TypesSQLite.integer.value,
            'name': TypesSQLite.text.value,
            'tick': TypesSQLite.text.value,
            'following_resource': TypesSQLite.text.value,
            'course_following': TypesSQLite.real.value,
            'capitalization': TypesSQLite.integer.value,
            'emission': TypesSQLite.real.value,
            'currency_index': TypesSQLite.real.value
        })

        await self.create_table('currency_emission_requests', {
            'number_match': TypesSQLite.integer.value,
            'telegram_id': TypesSQLite.integer.value,
            'country_id': TypesSQLite.integer.value,
            'name_currency': TypesSQLite.text.value,
            'tick_currency': TypesSQLite.text.value,
            'following_resource': TypesSQLite.text.value,
            'course_following': TypesSQLite.real.value,
            'capitalization': TypesSQLite.integer.value,
            'amount_emission_currency': TypesSQLite.real.value,
            'date_request_creation': TypesSQLite.text.value,
            'status_confirmed': TypesSQLite.blob.value,
            'date_confirmed': TypesSQLite.text.value
        })

        # Добавление стран
        country_names = await match_db.extraction_names_countries(type_match)
        for name_country in country_names:
            await self.insert(
                'countries',
                ['name', 'admin'],
                (name_country, False)
            )


class MatchService:
    """Сервис для управления матчами."""

    def __init__(self, master_db: MasterDatabase):
        self.master_db = master_db

    async def create_match(self, number_match: int, type_match: str):
        """Создает новый матч с необходимыми таблицами и данными."""
        await self.master_db.add_match(number_match, type_match)
        match_db_instance = MatchDatabase(number_match)
        await match_db_instance.initialize(type_match)

    async def delete_match(self, number_match: int) -> bool:
        """Удаляет матч из мастер-базы и соответствующую базу данных."""
        success = await self.master_db.delete_match_record(number_match)
        if not success:
            return False

        db_path = f'database/{number_match}.db'
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
                print(f"База данных {db_path} успешно удалена.")
                return True
            else:
                print(f"Файл {db_path} не найден.")
                return False
        except Exception as e:
            print(f"Ошибка при удалении файла базы данных {db_path}: {e}")
            return False

    async def match_exists(self, number_match: int) -> bool:
        """Проверяет, существует ли матч с данным номером."""
        return await self.master_db.match_exists(number_match)

    async def get_all_match_numbers(self) -> List[int]:
        """Возвращает список всех номеров матчей."""
        return await self.master_db.get_all_match_numbers()


class UserService:
    """Сервис для управления пользователями."""

    def __init__(self, master_db: MasterDatabase):
        self.master_db = master_db

    async def initialize_users(self):
        """Инициализирует таблицу пользователей."""
        await self.master_db.initialize_users()

    async def set_admin(self, telegram_id: int):
        """Устанавливает пользователя как администратора."""
        await self.master_db.add_admin(telegram_id)

    async def get_admin_telegram_id(self) -> Optional[int]:
        """Возвращает Telegram ID администратора."""
        return await self.master_db.get_admin_telegram_id()


