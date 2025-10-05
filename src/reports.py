import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def save_report(filename: Optional[str] = None):
    """
    Декоратор для сохранения результата функции-отчета в файл.
    Если имя файла не передано, используется имя по умолчанию reports_<date>.json
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            file_to_save = filename or f"reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(file_to_save, "w", encoding="utf-8") as f:
                f.write(result)

            logger.info(f"Отчет сохранён в файл: {file_to_save}")
            return result

        return wrapper
    return decorator


@save_report()  # По умолчанию будет писать в reports_<date>.json
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> str:
    """
    Возвращает траты по заданной категории за последние 3 месяца от переданной даты.

    Args:
        transactions (pd.DataFrame): Датафрейм с транзакциями.
        category (str): Название категории.
        date (str, optional): Дата в формате "YYYY-MM-DD". По умолчанию текущая дата.

    Returns:
        str: JSON-строка с суммой трат по категории.
    """
    if date:
        end_date = datetime.strptime(date, "%Y-%m-%d")
    else:
        end_date = datetime.now()

    start_date = end_date - timedelta(days=90)

    logger.info(f"Анализ категории '{category}' за период {start_date.date()} - {end_date.date()}")

    filtered = transactions[
        (pd.to_datetime(transactions["Дата операции"]) >= start_date) &
        (pd.to_datetime(transactions["Дата операции"]) <= end_date) &
        (transactions["Категория"] == category)
    ]

    total_spent = filtered["Сумма платежа"].sum()

    result = {"category": category, "total_spent": round(float(total_spent), 2)}

    logger.info(f"Траты по категории '{category}': {result['total_spent']}")

    return json.dumps(result, ensure_ascii=False, indent=2)
