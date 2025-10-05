from src.utils import read_transactions


def test_read_transactions_valid(tmp_path):
    file = tmp_path / "test.json"
    file.write_text('[{"id": 1, "state": "EXECUTED"}]', encoding="utf-8")

    result = read_transactions(str(file))
    assert result == [{"id": 1, "state": "EXECUTED"}]


def test_read_transactions_invalid(tmp_path):
    file = tmp_path / "test.json"
    file.write_text('{"id": 1}', encoding="utf-8")  # не список

    result = read_transactions(str(file))
    assert result == []


def test_read_transactions_missing():
    result = read_transactions("no_such_file.json")
    assert result == []
