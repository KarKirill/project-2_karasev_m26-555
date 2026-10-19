from functools import wraps


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
