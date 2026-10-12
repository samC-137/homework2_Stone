import shlex

from primitive_db.constants import VALID_TYPES


def tokenize(command: str) -> list[str]:
    """Split a command into words and SQL punctuation."""
    lexer = shlex.shlex(command, posix=True, punctuation_chars="(),=")
    lexer.whitespace_split = True
    return list(lexer)


def parse_columns(tokens: list[str]) -> dict[str, str]:
    """Parse column:type declarations from a create command."""
    columns = {}
    cleaned = [token for token in tokens if token not in {"(", ")", ","}]
    index = 0
    while index < len(cleaned):
        token = cleaned[index]
        if ":" in token:
            column, type_name = token.split(":", 1)
        elif index + 1 < len(cleaned):
            column, type_name = token, cleaned[index + 1]
            index += 1
        else:
            raise ValueError(f"Некорректное описание столбца: {token}")
        if type_name not in VALID_TYPES:
            raise ValueError(f"Неизвестный тип данных: {type_name}")
        columns[column] = type_name
        index += 1
    return columns


def parse_insert_values(tokens: list[str], schema: dict[str, str]) -> list[object]:
    """Parse positional values for an insert command."""
    values = [token for token in tokens if token not in {"(", ")", ","}]
    columns = [column for column in schema if column != "ID"]
    if len(values) != len(columns):
        raise ValueError("Количество значений не совпадает с числом столбцов")
    return [_convert_value(value, schema[column]) for column, value in zip(columns, values)]


def parse_conditions(tokens: list[str], schema: dict[str, str]) -> dict[str, object]:
    """Parse column=value conditions separated by and or commas."""
    conditions = {}
    index = 0
    while index < len(tokens):
        if tokens[index].lower() in {"and", ","}:
            index += 1
            continue
        if index + 2 >= len(tokens) or tokens[index + 1] != "=":
            raise ValueError("Условие должно иметь формат столбец = значение")
        column, raw_value = tokens[index], tokens[index + 2]
        if column not in schema:
            raise KeyError(f"Столбец {column} не найден")
        conditions[column] = _convert_value(raw_value, schema[column])
        index += 3
    return conditions


def split_keyword(tokens: list[str], keyword: str) -> tuple[list[str], list[str]]:
    """Split command arguments at a keyword, ignoring keyword case."""
    for index, token in enumerate(tokens):
        if token.lower() == keyword:
            return tokens[:index], tokens[index + 1 :]
    return tokens, []


def _convert_value(value: str, type_name: str) -> object:
    if type_name == "str":
        return value
    if type_name == "bool":
        normalized = value.lower()
        if normalized not in {"true", "false"}:
            raise ValueError(f"Ожидалось true или false, получено: {value}")
        return normalized == "true"
    try:
        return VALID_TYPES[type_name](value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"Неверное значение {value} для типа {type_name}") from error
