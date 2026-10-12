# Primitive DB

Консольная база данных с хранением таблиц в JSON-файлах.

## Запуск

```bash
uv sync
uv run database
```

## Команды

```text
create table users (name:str, age:int, active:bool)
list_tables
info users
insert into users values ("Анна", 20, true)
select from users
select from users where age=20
update users set age=21 where ID=1
delete from users where ID=1
drop table users
help
exit
```

Типы столбцов: `int`, `str`, `float`, `bool`. ID создаётся автоматически. Для `delete` и `drop` программа запрашивает подтверждение (`y` или `n`).

## Демонстрация

[![asciicast](https://asciinema.org/a/spZmk32rWG40KS7e.svg)](https://asciinema.org/a/spZmk32rWG40KS7e)
