from tortoise import fields
from tortoise.models import Model
from app.DatabaseWork.control_db import DatabaseManager
from app.DatabaseWork.control_db import init_match_db, close_db
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


# ---------------------
# Определение моделей
# ---------------------
class Countries(Model):
    id = fields.IntField(pk=True)
    economic_zone = fields.CharField(max_length=100)
    country_name = fields.CharField(max_length=100)
    telegram_id = fields.IntField(default=0)
    admin = fields.BooleanField(default=False)
    imf = fields.BooleanField(default=False)


class CountryChoiceRequests(Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.IntField()
    number_match = fields.IntField()
    country_name = fields.CharField(max_length=50)
    unique_word = fields.CharField(max_length=15, unique=True)
    admin_decision_message_id = fields.IntField()


class Currencies(Model):
    id = fields.IntField(pk=True)
    country = fields.ForeignKeyField('models.Countries', related_name='currencies')
    currency_name = fields.CharField(max_length=50)
    currency_tick = fields.CharField(max_length=10, unique=True)
    capitalization = fields.IntField()
    emission = fields.FloatField()
    current_amount = fields.FloatField()
    current_course = fields.FloatField()


class CurrencyEmissionRequests(Model):
    id = fields.IntField(pk=True)
    number_match = fields.IntField()
    telegram_id = fields.IntField()
    country_id = fields.ForeignKeyField('models.Countries', related_name='currency_emission_requests')
    currency_name = fields.CharField(max_length=50)
    currency_tick = fields.CharField(max_length=10)
    capitalization = fields.IntField()
    amount_emission_currency = fields.FloatField()
    date_request_creation = fields.DatetimeField(auto_now_add=True)
    status_confirmed = fields.BooleanField(default=False)
    date_confirmed = fields.DatetimeField(null=True)
    message_id_delete = fields.IntField(null=True)


class BankTransferRequests(Model):
    id = fields.IntField(pk=True)
    number_match = fields.IntField()
    payer_country_id = fields.ForeignKeyField('models.Countries', related_name='payer_transfers')
    beneficiary_country_id = fields.ForeignKeyField('models.Countries', related_name='beneficiary_transfers')
    currency_id = fields.ForeignKeyField('models.Currencies', related_name='transfers')
    amount_currency_transfer = fields.FloatField()
    comment = fields.TextField(null=True)
    date_request_creation = fields.DatetimeField(auto_now_add=True)
    status_cancelled = fields.BooleanField(default=False)
    date_cancelled = fields.DatetimeField(null=True)


# ---------------------
# Менеджеры таблиц
# ---------------------
class MatchManager(DatabaseManager):
    async def initialize_match(self, number_match: int, id_user_owner_match: int, type_map: dict):
        """Создает новую базу данных для матча и инициализирует таблицы."""
        try:
            await init_match_db(number_match=number_match)

            countries = []
            imf_country_name = None  # Переменная для страны IMF

            # Разворачиваем frozenset в обычный список
            for region_dict in type_map.get('Великая война', []):
                for region_name, country_list in region_dict.items():
                    for country_name in country_list:
                        countries.append({
                            'economic_zone': region_name,  # Экономическая зона (регион)
                            'country_name': country_name,  # Название страны
                            'telegram_id': id_user_owner_match if region_name == "IMF" else 0,  # Присваиваем владельцу, если это IMF
                            'admin': False,  # Админские привилегии
                            'imf': True if region_name == "IMF" else False
                        })

                        if region_name == "IMF":
                            imf_country_name = country_name

            await self.insert(Countries, countries)

            # Если IMF есть, создаем валюту virtual_silver (VS) для этой страны
            if imf_country_name:
                imf_country_obj = await Countries.get(country_name=imf_country_name)  # Получаем объект страны IMF

                currencies = [
                    {
                        'country_id': imf_country_obj.id,  # Передаем объект страны
                        'currency_name': 'virtual_silver',
                        'currency_tick': 'VS',
                        'capitalization': 10000000,
                        'emission': 10000000,
                        'current_amount': 10000000,
                        'current_course': 1.0
                    }
                ]
                await self.insert(Currencies, currencies)
        finally:
            await close_db()

