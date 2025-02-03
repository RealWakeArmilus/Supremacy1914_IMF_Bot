import asyncio
import logging
import sys
from app.config import bot, dp
from app.scheduler import run_scheduler
from app.handlers import router


# Вывод действий бота в консоль
def log_processing(state_status : bool):
    """
    :param state_status: Вкл/Выкл - включать при debug, выключать при продакшене
    """

    if state_status:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)


async def main():
    # Посредник между файлами run.py и handlers.py
    dp.include_router(router)

    # Запуск планировщика
    asyncio.create_task(run_scheduler())

    # Запуск бота
    await dp.start_polling(bot)


if __name__ == "__main__":

    view_logger = True

    log_processing(view_logger)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
