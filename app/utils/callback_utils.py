from asyncio.log import logger
from aiogram.types import Message, CallbackQuery


def parse_callback_data(callback_data: str, prefix: str) -> list[str]:
    """Extract data parts from callback data based on a prefix."""
    return callback_data.split(f"{prefix}_")[-1].split('_')


def get_number_match_from_callback_data(data: str, prefix: str) -> str:
    """Extract number match from callback data based on a prefix."""
    return data.split(f"{prefix}_")[-1]


async def handle_error(callback: CallbackQuery, error: Exception, message: str):
    """Log an error and notify the user."""
    logger.error(f"Error: {error}")
    await send_edit_message(callback, message)


async def handle_exception(callback_or_message, section, error, custom_message="Произошла ошибка. Повторите позже."):
    """Handle exceptions and notify the user."""
    logger.error(f"Exception {section}: {error}", exc_info=True)
    if isinstance(callback_or_message, CallbackQuery):
        await callback_or_message.answer(f'{custom_message} {error}', show_alert=True)
    elif isinstance(callback_or_message, Message):
        await callback_or_message.answer(f'{custom_message} {error}', parse_mode="html")


async def send_formatted_message(target, template, **kwargs):
    """Send a formatted message with dynamic data."""
    message = template.format(**kwargs)
    if isinstance(target, CallbackQuery):
        await send_edit_message(target, message)
    elif isinstance(target, Message):
        await target.edit_text(message, parse_mode="html")


async def send_edit_message(callback: CallbackQuery, text: str, markup=None) -> int:
    """
    Edit the edit message for the callback query.

    :return: message.message_id
    """
    message = await callback.message.edit_text(text, reply_markup=markup, parse_mode="html")

    return message.message_id


async def send_message(callback: CallbackQuery, text: str, markup=None):
    """
    Edit the edit message for the callback query.

    :return: message.message_id
    """
    message = await callback.message.answer(text, reply_markup=markup, parse_mode="html")

    return message.message_id


async def notify_user(callback: CallbackQuery, text: str):
    """Send a notification to the user."""
    await callback.answer(text)
