from primitive_db.constants import ID_COLUMN, VALID_TYPES


def create_table(
    metadata: dict, table_name: str, columns: dict[str, str]
) -> dict:
    """Add a validated table schema to metadata."""
    if table_name in metadata:
        raise ValueError(f"Таблица {table_name} уже существует")
    if not table_name.isidentifier():
        raise ValueError("Некорректное имя таблицы")
    if not columns:
        raise ValueError("В таблице должен быть хотя бы один столбец")
    if ID_COLUMN in columns:
        raise ValueError(f"Столбец {ID_COLUMN} создается автоматически")
    for column, type_name in columns.items():
        if not column.isidentifier():
            raise ValueError(f"Некорректное имя столбца: {column}")
        if type_name not in VALID_TYPES:
            raise ValueError(f"Неизвестный тип данных: {type_name}")
    metadata[table_name] = {ID_COLUMN: "int", **columns}
    return metadata


def drop_table(metadata: dict, table_name: str) -> dict:
    """Remove a table schema from metadata."""
    if table_name not in metadata:
        raise KeyError(f"Таблица {table_name} не найдена")
    del metadata[table_name]
    return metadata


def list_tables(metadata: dict) -> list[str]:
    """Return table names in sorted order."""
    return sorted(metadata)


def insert(
    metadata: dict,
    table_name: str,
    values: list[object],
    table_data: list[dict],
) -> list[dict]:
    """Validate and append one record, assigning its ID."""
    schema = _get_schema(metadata, table_name)
    columns = [column for column in schema if column != ID_COLUMN]
    if len(values) != len(columns):
        raise ValueError("Количество значений не совпадает с числом столбцов")
    row = {ID_COLUMN: max((item[ID_COLUMN] for item in table_data), default=0) + 1}
    for column, value in zip(columns, values):
        _validate_value(column, value, schema[column])
        row[column] = value
    return [*table_data, row]


def select(
    table_data: list[dict], where_clause: dict[str, object] | None = None
) -> list[dict]:
    """Return all records or records matching a condition."""
    conditions = where_clause or {}
    return [row for row in table_data if _matches(row, conditions)]


def update(
    table_data: list[dict],
    set_clause: dict[str, object],
    where_clause: dict[str, object],
    schema: dict[str, str],
) -> list[dict]:
    """Update records matching a condition and return the changed data."""
    if not set_clause:
        raise ValueError("Не указаны новые значения")
    if ID_COLUMN in set_clause:
        raise ValueError(f"Столбец {ID_COLUMN} нельзя изменять")
    _validate_clause(schema, set_clause)
    _validate_clause(schema, where_clause)
    for row in table_data:
        if _matches(row, where_clause):
            row.update(set_clause)
    return table_data


def delete(
    table_data: list[dict], where_clause: dict[str, object]
) -> list[dict]:
    """Return records that do not match the deletion condition."""
    return [row for row in table_data if not _matches(row, where_clause)]


def _get_schema(metadata: dict, table_name: str) -> dict[str, str]:
    if table_name not in metadata:
        raise KeyError(f"Таблица {table_name} не найдена")
    return metadata[table_name]


def _validate_clause(schema: dict[str, str], values: dict[str, object]) -> None:
    for column, value in values.items():
        if column not in schema:
            raise KeyError(f"Столбец {column} не найден")
        _validate_value(column, value, schema[column])


def _validate_value(column: str, value: object, type_name: str) -> None:
    if type(value) is not VALID_TYPES[type_name]:
        raise ValueError(f"Столбец {column} должен иметь тип {type_name}")


def _matches(row: dict, conditions: dict[str, object]) -> bool:
    return all(row.get(column) == value for column, value in conditions.items())
