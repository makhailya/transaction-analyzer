import json
import logging
import random
from pathlib import Path
from typing import Any, Dict, List

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("logs/utils.log", mode="w", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def read_transactions(file_path: str) -> list[dict[str, Any]]:
    """
    Читает JSON-файл с транзакциями.
    Возвращает список транзакций или пустой список при ошибке.
    """
    path = Path(file_path)
    if not path.exists():
        logger.error("Файл не найден: %s", file_path)
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                logger.error("Некорректный формат данных в файле: %s", file_path)
                return []
            logger.debug("Успешно загружено %d транзакций из %s", len(data), file_path)
            return data
    except json.JSONDecodeError as e:
        logger.error("Ошибка чтения JSON в %s: %s", file_path, e)
        return []


def get_currency_rates(currencies: List[str]) -> List[Dict[str, Any]]:
    """Фиктивные данные о курсах валют (позже можно заменить на API)."""
    return [{"currency": cur, "rate": round(random.uniform(70, 100), 2)} for cur in currencies]


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """Фиктивные данные о ценах акций (позже можно заменить на API)."""
    return [{"stock": s, "price": round(random.uniform(100, 3000), 2)} for s in stocks]
