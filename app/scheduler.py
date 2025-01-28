import asyncio, logging
import aiofiles
import schedule

from app.multi_task import asyncio_gather
from app.DatabaseWork.database import DatabaseManager

logger = logging.getLogger(__name__)

db_master_manager = DatabaseManager()


async def master_db_exists() -> bool:
    """возвращает true если существует master.db"""
    try:
        async with aiofiles.open('database/master.db', mode='r'):
            return True
    except FileNotFoundError:
        return False


async def update_course_currency_for_alone_match(number_match: str):
    """Обновляет курсы валют для одного матча."""
    try:
        db_number_match_manager = DatabaseManager(database_path=number_match)
        data_currencies: list[dict] | None = await db_number_match_manager.get_all_data_currencies()

        if not data_currencies:
            raise Exception(f'Список валют пуст')

        for data_currency in data_currencies:
            if data_currency:
                await db_number_match_manager.update_course_alone_currency(data_currency=data_currency)
    except Exception as error:
        logger.error(f"Ошибка при обновлении курсов валют для № match: {number_match}: {error}")


async def async_update_course_currency_for_all_match():
    """Асинхронное обновление курсов валют во всех текущих матчах."""
    logger.info('Запуск процесса: обновления курсов валют, во всех текущих матчах.')

    try:
        if not await master_db_exists():
            raise Exception('Master.db не создана')

        all_match_numbers: list[str] | None = await db_master_manager.get_all_match_numbers()

        if not all_match_numbers:
            raise Exception('Список матчей в master.db пустой')

        tasks = [
            lambda match=number_match: update_course_currency_for_alone_match(number_match=match)
            for number_match in all_match_numbers
        ]

        await asyncio_gather(tasks=tasks, max_concurrent=4)
    except Exception as error:
        logger.error(f"Ошибка при обновлении курсов валют: {error}")


def update_course_currency_for_all_match():
    """Синхронная обёртка для вызова асинхронной функции async_update_course_currency_all_match"""
    asyncio.create_task(async_update_course_currency_for_all_match())


async def schedule_runner():
    """Асинхронный планировщик всех задач"""
    schedule.every(10).seconds.do(update_course_currency_for_all_match)

    while True:
        schedule.run_pending()  # Запуск отложенных задач
        await asyncio.sleep(1)  # Асинхронное ожидание вместо time.sleep


async def run_scheduler():
    """Асинхронная обёртка для запуска планировщика"""
    await schedule_runner()


