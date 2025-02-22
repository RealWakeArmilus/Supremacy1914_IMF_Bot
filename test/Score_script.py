import os
import objgraph
import logging
import asyncio
from datetime import datetime
import pytz
from io import StringIO

logger = logging.getLogger(__name__)

# Директория для сохранения файлов
directory = os.path.join(os.path.dirname(__file__), 'pics')

object_names = ('tuple', 'dict', 'list')

# Запоминаем время старта
timezone = pytz.timezone("Europe/Moscow")
start_time = datetime.now(timezone)


async def analyze():
    """Анализ утечек памяти"""
    time_elapsed = int((datetime.now(timezone) - start_time).total_seconds())
    fname_template = os.path.join(directory, f'poller_{time_elapsed}_%s.png')

    file = StringIO()
    file.write(f'{time_elapsed} с запуска, сохранил в "{fname_template}"')

    new_ids = objgraph.get_new_ids(limit=10, file=file)

    found = any(name in new_ids for name in object_names)
    if not found:
        return

    for name in object_names:
        new_obj_ids = new_ids.get(name, [])
        if len(new_obj_ids) < 50:
            continue
        new_objs = objgraph.at_addrs(new_obj_ids)
        objgraph.show_backrefs(new_objs[:10], filename=fname_template % name, shortnames=False)

    logger.info(file.getvalue())


async def analyze_loop():
    """Запускает анализ утечек памяти каждые 10 минут"""
    objgraph.get_new_ids()
    objgraph.get_new_ids()
    await asyncio.sleep(10)  # Первоначальная задержка

    while True:
        logging.info('Запускаю анализ памяти...')
        await analyze()
        await asyncio.sleep(600)  # Каждые 10 минут



