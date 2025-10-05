import json

import pandas as pd
import pytest

from src.views import greeting_by_time, main_page


@pytest.fixture
def sample_transactions():
    data = {
        "Дата операции": ["2025-09-01", "2025-09-05", "2025-09-07", "2025-09-10", "2025-09-12"],
        "Номер карты": ["1234", "1234", "5678", "5678", "5678"],
        "Сумма платежа": [500, 1500, 200, 3000, 700],
        "Категория": ["Супермаркеты", "Фастфуд", "Развлечения", "Переводы", "Медицина"],
        "Описание": ["Лента", "KFC", "Кинотеатр", "Перевод Валерий А.", "Аптека"]
    }
    return pd.DataFrame(data)


@pytest.fixture
def user_settings():
    return {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "AMZN"]
    }


def test_greeting_by_time():
    assert greeting_by_time("2025-09-26 08:00:00") == "Доброе утро"
    assert greeting_by_time("2025-09-26 14:00:00") == "Добрый день"
    assert greeting_by_time("2025-09-26 19:00:00") == "Добрый вечер"
    assert greeting_by_time("2025-09-26 02:00:00") == "Доброй ночи"


def test_main_page(sample_transactions, user_settings):
    result = main_page("2025-09-15 10:00:00", sample_transactions, user_settings)
    data = json.loads(result)

    assert "greeting" in data
    assert "cards" in data
    assert "top_transactions" in data
    assert "currency_rates" in data
    assert "stock_prices" in data
    assert len(data["cards"]) > 0
    assert len(data["top_transactions"]) <= 5
