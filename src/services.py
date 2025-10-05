import json
import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> str:
    """
    Рассчитывает сумму, которую можно накопить в 'Инвесткопилке'
    за заданный месяц.

    :param month: месяц в формате "YYYY-MM"
    :param transactions: список транзакций (каждая транзакция — словарь)
    :param limit: предел округления (например, 10, 50 или 100 ₽)
    :return: JSON-строка с результатом {"month": "...", "saved": ...}
    """
    saved_amount = 0.0
    for t in transactions:
        date_str = t.get("Дата операции")
        amount = t.get("Сумма операции")

        if not date_str or not amount:
            continue

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            logger.error("Некорректная дата в транзакции: %s", date_str)
            continue

        if date.strftime("%Y-%m") != month:
            continue

        if isinstance(amount, (int, float)):
            rounded = ((amount + limit - 1) // limit) * limit
            saved_amount += rounded - amount

    result = {"month": month, "saved": round(saved_amount, 2)}
    logger.debug("Инвесткопилка: %s", result)
    return json.dumps(result, ensure_ascii=False, indent=2)


def simple_search(query: str, transactions: List[Dict[str, Any]]) -> str:
    """
    Ищет транзакции, где query встречается в описании или категории.

    Args:
        query (str): строка для поиска
        transactions (list[dict]): список транзакций

    Returns:
        str: JSON со списком найденных транзакций
    """
    if not query:
        logger.warning("Запрос пустой")
        return json.dumps([])

    result = [
        tx for tx in transactions
        if (query.lower() in str(tx.get("Описание", "")).lower()
            or query.lower() in str(tx.get("Категория", "")).lower())
    ]

    logger.info("Найдено %s транзакций по запросу '%s'", len(result), query)
    return json.dumps(result, ensure_ascii=False, indent=2)
