import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.reports import save_report, spending_by_category


@pytest.fixture
def fake_df() -> pd.DataFrame:
    data = {
        "Дата операции": ["2025-09-01", "2025-09-05", "2025-09-10", "2025-09-15"],
        "Категория": ["Еда", "Еда", "Транспорт", "Еда"],
        "Сумма платежа": [100, 50, 200, 150],
    }
    return pd.DataFrame(data)


def test_spending_by_category(fake_df: pd.DataFrame) -> None:
    from src.reports import spending_by_category
    total = spending_by_category(fake_df, "Еда")
    assert total == 300


@pytest.fixture
def sample_transactions() -> pd.DataFrame:
    data = {
        "Дата операции": ["2025-07-01", "2025-08-15", "2025-09-10", "2025-09-20"],
        "Категория": ["Супермаркеты", "Фастфуд", "Супермаркеты", "Развлечения"],
        "Сумма платежа": [1000, 500, 2000, 1500],
    }
    return pd.DataFrame(data)


def test_spending_by_category_no_data(sample_transactions: pd.DataFrame) -> None:
    result = spending_by_category(sample_transactions, "Медицина", "2025-09-30")
    data = json.loads(result)
    assert data["category"] == "Медицина"
    assert data["total_spent"] == 0.0


def test_spending_by_category_with_data(sample_transactions: pd.DataFrame) -> None:
    result = spending_by_category(sample_transactions, "Супермаркеты", "2025-09-30")
    data = json.loads(result)
    assert data["category"] == "Супермаркеты"
    assert data["total_spent"] == 3000.0


@patch("src.reports.logger")
def test_logging_mock(mock_logger: MagicMock, sample_transactions: pd.DataFrame) -> None:
    spending_by_category(sample_transactions, "Супермаркеты", "2025-09-30")

    # Проверяем, что логгер вызывался
    assert mock_logger.info.call_count >= 2
    mock_logger.info.assert_any_call("Траты по категории 'Супермаркеты': 3000.0")


def test_spending_by_category_saves_file(tmp_path: Path, sample_transactions: pd.DataFrame) -> None:
    """Проверяем, что файл создается"""
    file_path = tmp_path / "custom_report.json"

    @save_report(str(file_path))
    def fake_report(*_: object, **__: object) -> str:
        return '{"test": 123}'

    fake_report(sample_transactions, "Супермаркеты", "2025-09-30")

    assert file_path.exists()

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["test"] == 123


@patch("src.reports.logger")
def test_spending_by_category_logging(mock_logger: MagicMock, sample_transactions: pd.DataFrame) -> None:
    spending_by_category(sample_transactions, "Супермаркеты", "2025-09-30")
    assert mock_logger.info.call_count >= 2
