import asyncio
import logging
import aiofiles
import schedule
import pytz
from datetime import datetime


from app.DatabaseWork.database import DatabaseManager

logger = logging.getLogger(__name__)

db_master_manager = DatabaseManager()


async def master_db_exists() -> bool:
    """Проверяет, существует ли master.db"""
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
            raise ValueError(f'№ матча {number_match} - список валют пуст.')

        for data_currency in data_currencies:
            if data_currency:
                await db_number_match_manager.update_course_alone_currency(data_currency=data_currency)
                await view_runner_update_course_currency(message=f"№ матча {number_match}")

    except Exception as error:
        await view_runner_update_course_currency(message=f"{error}", error=True)

    finally:
        del data_currencies


async def async_update_course_currency_for_all_match():
    """Асинхронное обновление курсов валют во всех текущих матчах."""
    try:
        if not await master_db_exists():
            raise ValueError('Master.db не создана')

        all_match_numbers: list[str] | None = await db_master_manager.get_all_match_numbers()

        if not all_match_numbers:
            raise ValueError('Список матчей в master.db пуст')

        await asyncio.gather(*(update_course_currency_for_alone_match(number_match) for number_match in all_match_numbers))

    except Exception as error:
        await view_runner_update_course_currency(message=f"{error}", error=True)

    finally:
        del all_match_numbers


def update_course_currency_for_all_match():
    """Синхронная обертка для вызова асинхронной функции async_update_course_currency_for_all_match"""
    asyncio.create_task(async_update_course_currency_for_all_match())


async def view_runner_update_course_currency(message : str, error : bool = False):
    """Запись логов запуска обновления валют"""
    timezone = pytz.timezone("Europe/Moscow")
    now_date = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")

    async with aiofiles.open('update_course_currency.log', mode='a', encoding='utf-8') as log_file:
        if message:
            await log_file.write(f"{now_date} - Успешный запуск обновления курсов валют {message}.\n")
        elif error and message:
            await log_file.write(f"{now_date} - Ошибка: {message}\n")


async def async_view_pivo_mb():
    """Асинронная проверка загружиности диска"""
    import time
    from psutil import Process
    from humanfriendly import format_size

    proc = Process()
    with open('pivo', 'a') as file:
        print(time.ctime(), format_size(proc.memory_info().rss), file=file)


def view_pivo_mb():
    """Синхронная обертка для вызова асинхронной функции async_view_pivo_mb"""
    asyncio.create_task(async_view_pivo_mb())


async def schedule_runner():
    """Асинхронный планировщик всех задач"""
    schedule.every(5).hours.do(update_course_currency_for_all_match)
    schedule.every(30).minutes.do(view_pivo_mb)

    while True:
        schedule.run_pending() # Запуск отложенных задач
        await asyncio.sleep(1)  # ждем 1


async def run_scheduler():
    """Асинхронная обертка для запуска планировщика"""
    await schedule_runner()
