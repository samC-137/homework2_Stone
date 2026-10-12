import prompt
from prettytable import PrettyTable

from primitive_db import core
from primitive_db.constants import ID_COLUMN
from primitive_db.parser import (
    parse_columns,
    parse_conditions,
    parse_insert_values,
    split_keyword,
    tokenize,
)
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
    table_path,
)


def run() -> None:
    """Read and execute database commands until the user exits."""
    print("Введите команду. Для списка команд введите help.")
    while True:
        try:
            command = prompt.string(prompt=">>> Введите команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not command:
            continue
        try:
            if not execute(command):
                return
        except (KeyError, ValueError, FileNotFoundError) as error:
            print(f"Ошибка: {error}")


def execute(command: str) -> bool:
    """Execute one command and return false when the session should end."""
    tokens = tokenize(command)
    if not tokens:
        return True
    action = tokens[0].lower()
    arguments = tokens[1:]

    if action in {"exit", "quit"}:
        return False
    if action == "help":
        _print_help()
    elif action in {"create", "create_table"}:
        _create_table(arguments)
    elif action in {"drop", "drop_table"}:
        _drop_table(arguments)
    elif action in {"list_tables", "tables"}:
        print("\n".join(core.list_tables(load_metadata())) or "Таблиц нет")
    elif action == "insert":
        _insert(arguments)
    elif action == "select":
        _select(arguments)
    elif action == "update":
        _update(arguments)
    elif action == "delete":
        _delete(arguments)
    elif action == "info":
        _show_info(arguments)
    else:
        raise ValueError(f"Неизвестная команда: {action}. Введите help")
    return True


def _create_table(arguments: list[str]) -> None:
    if arguments and arguments[0].lower() == "table":
        arguments = arguments[1:]
    if not arguments:
        raise ValueError("Не указано имя таблицы")
    table_name, *column_tokens = arguments
    metadata = core.create_table(load_metadata(), table_name, parse_columns(column_tokens))
    save_metadata(metadata)
    save_table_data(table_name, [])
    print(f"Таблица {table_name} успешно создана")


def _drop_table(arguments: list[str]) -> None:
    if arguments and arguments[0].lower() == "table":
        arguments = arguments[1:]
    if len(arguments) != 1:
        raise ValueError("Укажите имя одной таблицы")
    table_name = arguments[0]
    metadata = core.drop_table(load_metadata(), table_name)
    save_metadata(metadata)
    table_path(table_name).unlink(missing_ok=True)
    print(f"Таблица {table_name} успешно удалена")


def _insert(arguments: list[str]) -> None:
    if len(arguments) < 3 or arguments[0].lower() != "into":
        raise ValueError("Использование: insert into <таблица> values (<значения>)")
    table_name = arguments[1]
    if arguments[2].lower() != "values":
        raise ValueError("После имени таблицы ожидается values")
    metadata = load_metadata()
    if table_name not in metadata:
        raise KeyError(f"Таблица {table_name} не найдена")
    values = parse_insert_values(arguments[3:], metadata[table_name])
    table_data = load_table_data(table_name)
    updated_data = core.insert(metadata, table_name, values, table_data)
    save_table_data(table_name, updated_data)
    print(f"Запись с ID={updated_data[-1][ID_COLUMN]} успешно добавлена в таблицу {table_name}.")


def _select(arguments: list[str]) -> None:
    if len(arguments) < 2 or arguments[0].lower() != "from":
        raise ValueError("Использование: select from <таблица> [where <условие>]")
    table_name, *condition_tokens = arguments[1:]
    metadata = load_metadata()
    if table_name not in metadata:
        raise KeyError(f"Таблица {table_name} не найдена")
    where_tokens = []
    if condition_tokens:
        keyword, where_tokens = split_keyword(condition_tokens, "where")
        if keyword:
            raise ValueError("Условие должно следовать за where")
    where_clause = parse_conditions(where_tokens, metadata[table_name])
    table_data = load_table_data(table_name)
    _print_rows(metadata[table_name], core.select(table_data, where_clause))


def _update(arguments: list[str]) -> None:
    if not arguments:
        raise ValueError("Использование: update <таблица> set ... where ...")
    table_name, *clauses = arguments
    metadata = load_metadata()
    if table_name not in metadata:
        raise KeyError(f"Таблица {table_name} не найдена")
    set_tokens, where_tokens = split_keyword(clauses, "where")
    if not where_tokens:
        raise ValueError("Для update укажите условие where")
    if not set_tokens or set_tokens[0].lower() != "set":
        raise ValueError("После имени таблицы ожидается set")
    set_clause = parse_conditions(set_tokens[1:], metadata[table_name])
    where_clause = parse_conditions(where_tokens, metadata[table_name])
    table_data = load_table_data(table_name)
    updated_data = core.update(
        table_data, set_clause, where_clause, metadata[table_name]
    )
    save_table_data(table_name, updated_data)
    print(f"Данные таблицы {table_name} успешно обновлены")


def _delete(arguments: list[str]) -> None:
    if len(arguments) < 4 or arguments[0].lower() != "from":
        raise ValueError("Использование: delete from <таблица> where <условие>")
    table_name, *clauses = arguments[1:]
    metadata = load_metadata()
    if table_name not in metadata:
        raise KeyError(f"Таблица {table_name} не найдена")
    before_where, where_tokens = split_keyword(clauses, "where")
    if before_where or not where_tokens:
        raise ValueError("Для delete укажите условие where")
    where_clause = parse_conditions(where_tokens, metadata[table_name])
    table_data = load_table_data(table_name)
    updated_data = core.delete(table_data, where_clause)
    save_table_data(table_name, updated_data)
    print(f"Записи из таблицы {table_name} успешно удалены")


def _show_info(arguments: list[str]) -> None:
    if len(arguments) != 1:
        raise ValueError("Использование: info <таблица>")
    table_name = arguments[0]
    metadata = load_metadata()
    if table_name not in metadata:
        raise KeyError(f"Таблица {table_name} не найдена")
    schema = metadata[table_name]
    rows = load_table_data(table_name)
    columns = ", ".join(f"{name}:{type_name}" for name, type_name in schema.items())
    print(f"Таблица: {table_name}\nСтолбцы: {columns}\nКоличество записей: {len(rows)}")


def _print_rows(schema: dict[str, str], rows: list[dict]) -> None:
    table = PrettyTable()
    table.field_names = list(schema)
    for row in rows:
        table.add_row([row[column] for column in schema])
    print(table)


def _print_help() -> None:
    print(
        "Команды:\n"
        "  create table <имя> (<столбец>:<тип>, ...)\n"
        "  drop table <имя>\n"
        "  list_tables\n"
        "  insert into <имя> values (<значение>, ...)\n"
        "  select from <имя> [where <столбец> = <значение>]\n"
        "  update <имя> set <столбец> = <значение> where <столбец> = <значение>\n"
        "  delete from <имя> where <столбец> = <значение>\n"
        "  info <имя>\n"
        "  help\n"
        "  exit"
    )
