from tortoise import Tortoise
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# ---------------------
# Инициализация ORM
# ---------------------
async def init_master_db():
    await Tortoise.init(
        db_url="sqlite://database/test_master.db",  # Главная база
        modules={"models": ["app.DatabaseWork.models_master"]}  # Только Match и User
    )
    await Tortoise.generate_schemas()

async def init_match_db(number_match: int):
    db_path = f"sqlite://database/{number_match}.db"  # Отдельная БД для матча
    await Tortoise.init(
        db_url=db_path,
        modules={"models": ["app.DatabaseWork.models_match"]}  # Только Countries и Currencies
    )
    await Tortoise.generate_schemas()


# ---------------------
# Отключение ORM
# ---------------------
async def close_db():
    await Tortoise.close_connections()


# ---------------------
# Менеджер базы данных
# ---------------------
class DatabaseManager:
    async def create(self, model, **fields):
        """Создает новую запись в таблице."""
        try:
            obj = await model.create(**fields)
            return obj
        except Exception as e:
            logger.error(f'Ошибка при создании {model.__name__}: {e}')
            return None

    async def insert(self, model, data: List[Dict[str, Any]]):
        """Вставка одной или нескольких записей."""
        try:
            if not data:
                raise ValueError("Данные для вставки пустые")
            await model.bulk_create([model(**item) for item in data])
        except Exception as e:
            logger.error(f'Ошибка при вставке данных в {model.__name__}: {e}')


    async def fetch_records(self, model, filters: Optional[Dict[str, Any]] = None, single: bool = False) \
    -> Optional[List[Dict[str, Any]]]:
        """
        Получение записей из базы.

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
