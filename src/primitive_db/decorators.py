import json
import time
from copy import deepcopy
from functools import wraps

import prompt


def handle_db_errors(func):
    '''Обрабатывает ошибки при выполнении команд базы данных.'''

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except FileExistsError as error:
            print(f'Ошибка: {error}')

        except KeyError as error:
            print(f'Ошибка: {error.args[0]}')

        except ValueError as error:
            message = str(error).rstrip('.')
            print(f'Некорректное значение: {message}. Попробуйте снова.')

        except OSError as error:
            print(f'Ошибка при работе с файлом: {error}')

        return None

    return wrapper


def confirm_action(action_name: str):
    '''Запрашивает подтверждение перед выполнением действия.'''

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            while True:
                answer = prompt.string(
                    f'Подтвердите действие "{action_name}" [y/n]: '
                ).strip().lower()

                if answer == 'y':
                    return func(*args, **kwargs)

                if answer == 'n':
                    print('Операция отменена.')
                    return False

                print('Введите y или n.')

        return wrapper

    return decorator


def log_time(func):
    '''Выводит время выполнения функции.'''

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()

        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - start
            print(
                f'Время выполнения {func.__name__}: '
                f'{elapsed:.6f} с'
            )

    return wrapper


def create_cacher():
    '''Создаёт декоратор для кэширования результатов функции.'''
    cache = {}

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = json.dumps(
                [args, kwargs],
                sort_keys=True,
                ensure_ascii=False
            )

            if key not in cache:
                result = func(*args, **kwargs)
                cache[key] = deepcopy(result)

            return deepcopy(cache[key])

        wrapper.clear_cache = cache.clear
        return wrapper

    return decorator
