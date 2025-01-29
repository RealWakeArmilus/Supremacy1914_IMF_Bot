import asyncio
import logging
from typing import Callable, Any, Awaitable, Iterable

logger = logging.getLogger(__name__)

# TODO есть альтернатива asyncio_gather это multiprocessing. Нужно изучить более подробно.

async def asyncio_gather(
        tasks: Iterable[Callable[[], Awaitable[Any]]],
        max_concurrent: int = 0
) -> list[Any]:
    """
    Универсальная функция для параллельного выполнения асинхронных задач.
    \nКогда стоит использовать asyncio.gather?
        \n1. Если ваши задачи зависят от ввода-вывода (например, чтение из базы данных, сетевые запросы).
        \n2. Если время обработки каждой задачи значительно варьируется.
        \n3. Если вы хотите ускорить обработку большого количества задач без увеличения нагрузки на систему.
    \n\nКогда не стоит использовать asyncio.gather?
        \n1. Если задачи требуют интенсивных вычислений (например, сложные математические расчёты). В таких случаях асинхронность не поможет, и лучше использовать multiprocessing.
        \n2. Если вы обрабатываете всего одну или две задачи, где параллелизм не даёт значительных преимуществ.

    \n\nПример использования
        for number_match in all_match_numbers:
            await asyncio_gather(
                tasks=[lambda match=number_match: update_course_for_alone_match(match)],
                max_concurrent=2
            )

    \n\nОбъяснение
    Что происходит:
        1. update_course_for_alone_match(number_match=number_match) сразу вызывается (поскольку это корутина).
        2. Результат выполнения этой корутины (а это Awaitable объект) передаётся в tasks.
        3. Внутри asyncio_gather предполагается, что tasks — это итерабельный объект функций, возвращающих корутины. Однако вместо этого туда попадает один Awaitable объект, что приводит к ошибке.

    \n\nЕще лучше использовать так:
        tasks = [
            lambda match=number_match: update_course_for_alone_match(match)
            for number_match in all_match_numbers]

        await asyncio_gather(tasks=tasks, max_concurrent=2)

    :param tasks: Итерабельный список функций (которые возвращают корутины).
    :param max_concurrent: Максимальное количество одновременных задач (0 = без ограничений).
    :return: Список результатов выполнения задач.
    """
    try:
        if max_concurrent > 0:
            semaphore = asyncio.Semaphore(max_concurrent)

            async def limited_task(task: Callable[[], Awaitable[Any]]) -> Any:
                async with semaphore:
                    return await task()

            return await asyncio.gather(*(limited_task(task) for task in tasks))
        else:
            return await asyncio.gather(*(task() for task in tasks))
    except Exception as error:
        logger.error(f"Ошибка при выполнении задач: {error}")
        raise



