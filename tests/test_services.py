import json
import logging

import pytest

from src.services import investment_bank, simple_search


@pytest.fixture
def sample_transactions():
    return [
        {"Дата операции": "2025-09-10", "Сумма операции": 1712},
        {"Дата операции": "2025-09-15", "Сумма операции": 243},   # округление от 243
        {"Дата операции": "2025-08-20", "Сумма операции": 500},   # другой месяц → игнор
        {"Дата операции": "2025-09-25", "Сумма операции": 999.5},  # нецелое число
        {"Дата операции": "ошибка", "Сумма операции": 100},       # некорректная дата
    ]


def test_investment_bank_basic(sample_transactions):
    result = investment_bank("2025-09", sample_transactions, 50)
    data = json.loads(result)

    assert data["month"] == "2025-09"
    # Проверяем округления:
    # 1712 → 1750 → 38
    # 243 → 250 → 7
    # 999.5 → 1000 → 0.5
    # итого = 45.5
    assert pytest.approx(data["saved"], 0.01) == 45.5


def test_investment_bank_different_limit(sample_transactions):
    result = investment_bank("2025-09", sample_transactions, 100)
    data = json.loads(result)

    # 1712 → 1800 → 88
    # 243 → 300 → 57
    # 999.5 → 1000 → 0.5
    # итого = 145.5
    assert pytest.approx(data["saved"], 0.01) == 145.5


def test_investment_bank_no_transactions():
    result = investment_bank("2025-07", [], 50)
    data = json.loads(result)

    assert data["month"] == "2025-07"
    assert data["saved"] == 0.0


def test_investment_bank_logs_error(sample_transactions, caplog):
    with caplog.at_level(logging.ERROR):
        investment_bank("2025-09", sample_transactions, 50)

    # Должна быть ошибка по транзакции с "Дата операции": "ошибка"
    error_logs = [rec for rec in caplog.records if rec.levelname == "ERROR"]
    assert any("ошибка" in rec.message for rec in error_logs)


@pytest.fixture
def sample_transactions_search():
    return [
        {"Дата операции": "2025-09-01", "Категория": "Супермаркеты", "Описание": "Лента"},
        {"Дата операции": "2025-09-05", "Категория": "Фастфуд", "Описание": "Макдональдс"},
        {"Дата операции": "2025-09-07", "Категория": "Развлечения", "Описание": "Кинотеатр"},
        {"Дата операции": "2025-09-10", "Категория": "Переводы", "Описание": "Валерий А."},
    ]


def test_simple_search_by_category(sample_transactions_search):
    result = simple_search("Супермаркеты", sample_transactions_search)
    data = json.loads(result)

    assert len(data) == 1
    assert data[0]["Описание"] == "Лента"


def test_simple_search_by_description(sample_transactions_search):
    result = simple_search("кино", sample_transactions_search)  # проверка нечувствительности к регистру
    data = json.loads(result)

    assert len(data) == 1
    assert data[0]["Категория"] == "Развлечения"


def test_simple_search_no_results(sample_transactions_search):
    result = simple_search("Аптека", sample_transactions_search)
    data = json.loads(result)

    assert data == []


def test_simple_search_empty_query_logs_warning(sample_transactions_search, caplog):
    with caplog.at_level(logging.WARNING):
        result = simple_search("", sample_transactions_search)

    assert json.loads(result) == []
    assert any("Запрос пустой" in rec.message for rec in caplog.records)
