from src.file_reader import read_transactions_csv, read_transactions_excel
from src.formatters import format_transaction
from src.processing import filter_by_state, sort_by_date
from src.search import process_bank_search
from src.utils import read_transactions


def main() -> None:
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла")
    print("2. Получить информацию о транзакциях из CSV-файла")
    print("3. Получить информацию о транзакциях из XLSX-файла")

    choice = input("Ваш выбор: ")
    if choice == "1":
        print("Для обработки выбран JSON-файл.")
        transactions = read_transactions("data/operations.json")
    elif choice == "2":
        print("Для обработки выбран CSV-файл.")
        transactions = read_transactions_csv("data/transactions.csv")
    elif choice == "3":
        print("Для обработки выбран XLSX-файл.")
        transactions = read_transactions_excel("data/transactions_excel.xlsx")
    else:
        print("Некорректный выбор.")
        return

    # фильтрация по статусу
    statuses = ["EXECUTED", "CANCELED", "PENDING"]
    while True:
        status = input(f"Введите статус ({', '.join(statuses)}): ").upper()
        if status in statuses:
            transactions = filter_by_state(transactions, status)
            print(f'Операции отфильтрованы по статусу "{status}"')
            break
        else:
            print(f'Статус операции "{status}" недоступен.')

    if not transactions:
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
        return

    # сортировка
    if input("Отсортировать операции по дате? Да/Нет ").lower() == "да":
        order = input("Отсортировать по возрастанию или по убыванию? ").lower()
        transactions = sort_by_date(transactions, reverse=(order == "по убыванию"))

    # только рублевые
    if input("Выводить только рублевые транзакции? Да/Нет ").lower() == "да":
        transactions = [tx for tx in transactions if tx.get("operationAmount",
                        {}).get("currency", {}).get("code") == "RUB"]

    # поиск по слову
    if input("Отфильтровать список транзакций по слову в описании? Да/Нет ").lower() == "да":
        word = input("Введите слово: ")
        transactions = process_bank_search(transactions, word)

    # вывод
    print("Распечатываю итоговый список транзакций...")

    print(f"\nВсего банковских операций в выборке: {len(transactions)}\n")
    print("Распечатываю итоговый список транзакций...")
    print(f"\nВсего банковских операций в выборке: {len(transactions)}\n")

    for tx in transactions:
        print(format_transaction(tx))
        print()  # пустая строка между транзакциями
