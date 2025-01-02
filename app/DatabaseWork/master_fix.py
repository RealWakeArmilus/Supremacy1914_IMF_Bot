import os
from typing import List, Optional

from SPyderSQL import AsyncSQLite
import app.DatabaseWork.match as match_db

# Constants
MASTER_DB_PATH = 'database/master.db'

SPyderSQLite = AsyncSQLite


class DatabaseManager:
    """Базовый менеджер для работы с SQLite базой данных."""

    def __init__(self, db_path: str):
        self.SPyderSQLite = SPyderSQLite(db_path)

    async def create_table(self, table_name: str, columns: dict):
        """Создает таблицу в базе данных."""
        await self.SPyderSQLite.create(
            name_table=table_name,
            append_columns=columns,
            id_primary_key=True
        ).execute()

    async def insert(self, table_name: str, columns: List[str], values: tuple):
        """Вставляет запись в таблицу."""
        await self.SPyderSQLite.insert(
            name_table=table_name,
            names_columns=columns
        ).execute(parameters=values)

    async def select(self, table_name: str, columns: List[str] = None, where_clause: dict = None):
        """Выбирает записи из таблицы."""
        if columns is None and where_clause:

            return await self.SPyderSQLite.select(
                name_table=table_name,
            ).where(where_clause).fetch_one()

        elif where_clause is None and columns:

            return await self.SPyderSQLite.select(
                name_table=table_name,
                names_columns=columns
            ).execute()

        elif None is (columns, where_clause):

            return await self.SPyderSQLite.select(
                name_table=table_name,
            ).execute()

        else:
            print('Error: SQLRequest select from DatabaseManager.master_fix in columns, where_clause == ?')

    async def delete(self, table_name: str, where_clause: dict):
        """Удаляет записи из таблицы."""
        await self.SPyderSQLite.delete(
            name_table=table_name,
        ).where(where_clause).execute()


class MasterDatabase(DatabaseManager):
    """Менеджер для мастер-базы данных."""

    def __init__(self, db_path: str = MASTER_DB_PATH):
        super().__init__(db_path)

    async def initialize(self):
        """Инициализирует необходимые таблицы в мастер-базе."""
        await self.create_table(
            table_name='match',
            columns={
                'number': 'INTEGER',
                'type_map': 'TEXT'
            }
        )

    async def add_match(self, number_match: int, type_match: str):
        """Добавляет новый матч в мастер-базу."""
        await self.insert(
            table_name='match',
            columns=['number', 'type_map'],
            values=(number_match, type_match)
        )

    async def match_exists(self, number: int) -> bool:
        """Проверяет существование матча по номеру."""
        return await self.select(
            table_name='match',
            where_clause={'number': number}
        )

    async def get_all_match_numbers(self) -> List[int]:
        """Возвращает список всех номеров матчей."""
        matches = await self.select(
            table_name='match',
            columns=['number']
        )
        return [match['number'] for match in matches]

    async def delete_match_record(self, number_match: str) -> bool:
        """Удаляет запись матча из мастер-базы."""
        try:
            await self.delete(
                table_name='match',
                where_clause={'number': number_match}
            )
            return True
        except Exception as e:
            print(f"Ошибка при удалении матча {number_match}: {e}")
            return False

    async def initialize_users(self):
        """Инициализирует таблицу пользователей."""
        await self.create_table(
            table_name='users',
            columns={
                'telegram_id': 'INTEGER',
                'admin': 'BLOB'
            }
        )

    async def add_admin(self, telegram_id: int):
        """Добавляет администратора в таблицу пользователей."""
        await self.insert(
            table_name='users',
            columns=['telegram_id', 'admin'],
            values=(telegram_id, True)
        )


    async def get_admin_telegram_id(self) -> Optional[int] | None:
        """Возвращает telegram_id администратора."""
        # TODO возвращает лишь одного, сделай так чтобы выводился список админов в будущем

        data_admin = await self.select(
            table_name='users',
            where_clause={'admin': True}
        )

        return data_admin['telegram_id']


class MatchDatabase(DatabaseManager):
    """Менеджер для базы данных конкретного матча."""

    def __init__(self, number_match: int):
        db_path = f'database/{number_match}.db'
        super().__init__(db_path)
        self.number_match = number_match

    async def initialize(self, type_match: str):
        """Инициализирует все необходимые таблицы для матча."""
        await self.create_table(
            table_name='countries',
            columns={
                'name': 'TEXT',
                'telegram_id': 'INTEGER',
                'admin': 'BLOB'
            }
        )

        await self.create_table(
            table_name='country_choice_requests',
            columns={
                'telegram_id': 'INTEGER',
                'number_match': 'INTEGER',
                'name_country': 'TEXT',
                'unique_word': 'TEXT',
                'admin_decision_message_id': 'INTEGER'
            }
        )

        await self.create_table(
            table_name='currency',
            columns={
                'country_id': 'INTEGER',
                'name': 'TEXT',
                'tick': 'TEXT',
                'following_resource': 'TEXT',
                'course_following': 'REAL',
                'capitalization': 'INTEGER',
                'emission': 'REAL',
                'currency_index': 'REAL'
            }
        )

        await self.create_table(
            table_name='currency_emission_requests',
            columns={
                'number_match': 'INTEGER',
                'telegram_id': 'INTEGER',
                'country_id': 'INTEGER',
                'name_currency': 'TEXT',
                'tick_currency': 'TEXT',
                'following_resource': 'TEXT',
                'course_following': 'REAL',
                'capitalization': 'INTEGER',
                'amount_emission_currency': 'REAL',
                'date_request_creation': 'TEXT',
                'status_confirmed': 'BLOB',
                'date_confirmed': 'TEXT'
            }
        )

        # Добавление стран
        country_names = await match_db.extraction_names_countries(type_match)
        for name_country in country_names:
            await self.insert(
                table_name='countries',
                columns=['name', 'admin'],
                values=(name_country, False)
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

    async def delete_match(self, number_match: str) -> bool:
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


