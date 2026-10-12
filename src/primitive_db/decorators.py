import time
from functools import wraps


def handle_db_errors(func):
    """Print database errors raised by a wrapped function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: файл данных не найден")
        except KeyError as error:
            print(f"Ошибка: таблица или столбец {error} не найдены")
        except ValueError as error:
            print(f"Ошибка валидации: {error}")
    return wrapper


def confirm_action(action_name: str):
    """Ask before running a potentially destructive operation."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if answer.strip().lower() != "y":
                print("Операция отменена")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Print the time spent in the wrapped function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - start_time
            print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд")

    return wrapper


def create_cacher():
    """Return a closure that caches values produced by callbacks."""
    cache = {}

    def cache_result(key, value_func):
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    return cache_result
