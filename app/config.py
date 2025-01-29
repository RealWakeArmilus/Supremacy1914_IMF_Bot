from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os


# Загружаем переменные из .env
load_dotenv()

# Получаем токен из переменной окружения
TOKEN_BOT = os.getenv("TELEGRAM_BOT_TOKEN")
print(f"Бот использует токен: {TOKEN_BOT[:5]}... (скрыт)")

TON_WALLET_SPACE = 'UQDfYF3iMQDxc_JZBuuU_5gotKtQ-f0rjaIuuuZFYHKsGjYt'
TON_WALLET_TONKEEPER = 'UQBjgJlI4tPRypKgiYQ3YWYXLrNSa4aW_lwlXCqDuo60XOA0'


bot = Bot(token=TOKEN_BOT)
dp = Dispatcher()
