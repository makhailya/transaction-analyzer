# src/views.py
import json
import logging
from datetime import datetime
from typing import Any, Dict

import pandas as pd

from src.utils import get_currency_rates, get_stock_prices

logger = logging.getLogger(__name__)


def greeting_by_time(date_str: str) -> str:
    """Возвращает приветствие в зависимости от времени суток."""
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    hour = dt.hour

    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def main_page(date_str: str, transactions: pd.DataFrame, settings: Dict[str, Any]) -> str:
    """
    Формирует JSON-ответ для страницы "Главная".

    Args:
        date_str (str): Дата и время в формате "YYYY-MM-DD HH:MM:SS".
        transactions (pd.DataFrame): Датафрейм с транзакциями.
        settings (dict): настройки с валютами и акциями (из user_settings.json).

    Returns:
        str: JSON-строка с данными для веб-страницы.
    """
    # Приветствие
    greeting = greeting_by_time(date_str)

    # Фильтруем операции с начала месяца по указанную дату
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    start_month = dt.replace(day=1)
    filtered = transactions[
        (pd.to_datetime(transactions["Дата операции"]) >= start_month) &
        (pd.to_datetime(transactions["Дата операции"]) <= dt)
        ]

    # Данные по картам
    cards = []
    for card, group in filtered.groupby("Номер карты"):
        total_spent = group["Сумма платежа"].sum()
        cashback = round(total_spent * 0.01, 2)
        cards.append({
            "last_digits": str(card)[-4:],
            "total_spent": round(total_spent, 2),
            "cashback": cashback
        })

    # Топ-5 транзакций по сумме платежа
    top_tx = (
        filtered.nlargest(5, "Сумма платежа")[["Дата операции", "Сумма платежа", "Категория", "Описание"]]
        .to_dict("records")
    )
    for tx in top_tx:
        tx["date"] = pd.to_datetime(tx["Дата операции"]).strftime("%d.%m.%Y")
        tx["amount"] = tx.pop("Сумма платежа")
        tx["category"] = tx.pop("Категория")
        tx["description"] = tx.pop("Описание")
        tx.pop("Дата операции")

    # Курсы валют и акции
    currency_rates = get_currency_rates(settings["user_currencies"])
    stock_prices = get_stock_prices(settings["user_stocks"])

    response = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_tx,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    logger.info("Главная страница собрана успешно")
    return json.dumps(response, ensure_ascii=False, indent=2)
