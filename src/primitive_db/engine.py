import shlex

import prompt

from primitive_db.constants import META_FILE
from primitive_db.core import (
    create_table,
    drop_table,
    list_tables,
)
from primitive_db.utils import load_metadata, save_metadata


def welcome() -> None:
    HELP = '''
<command> exit - выйти из программы
<command> help - справочная информация
    '''

    print('Первая попытка запустить проект!')
    print('\n***')
    print(HELP)

    while True:
        command = prompt.string(
            prompt='Введите команду: '
        ).strip().lower()

        match command:
            case 'help':
                print(HELP)

            case 'exit':
                print('Выход из программы.')
                break

            case _:
                print(f'Неизвестная команда: {command}')


def print_help():
    '''Выводит справку по командам.'''
    print('\n***База данных***')
    print('Функции:')
    print(
        '<command> create_table <имя_таблицы> '
        '<столбец1:тип> ... - создать таблицу'
    )
    print('<command> list_tables - показать список таблиц')
    print('<command> drop_table <имя_таблицы> - удалить таблицу')
    print('<command> help - справочная информация')
    print('<command> exit - выход из программы\n')


def run():
    '''Запускает основной цикл обработки команд.'''
    print_help()

    while True:
        try:
            metadata = load_metadata(META_FILE)
            user_input = prompt.string('\nВведите команду: ')
            args = shlex.split(user_input)

            if not args:
                continue

            command, *params = args

            if command == 'create_table':
                if len(params) < 2:
                    raise ValueError(
                        'укажите имя таблицы и столбцы'
                    )

                table_name, *columns = params
                create_table(metadata, table_name, columns)
                save_metadata(META_FILE, metadata)

                schema = metadata[table_name]
                description = ', '.join(
                    f'{name}:{column_type}'
                    for name, column_type in schema.items()
                )
                print(
                    f'Таблица "{table_name}" успешно создана '
                    f'со столбцами: {description}'
                )

            elif command == 'drop_table':
                if len(params) != 1:
                    raise ValueError('укажите имя таблицы')

                table_name = params[0]
                drop_table(metadata, table_name)
                save_metadata(META_FILE, metadata)
                print(f'Таблица "{table_name}" успешно удалена.')

            elif command == 'list_tables':
                if params:
                    raise ValueError('list_tables без аргументов')

                tables = list_tables(metadata)

                if not tables:
                    print('Таблиц пока нет.')
                else:
                    for table_name in tables:
                        print(f'- {table_name}')

            elif command == 'help':
                if params:
                    raise ValueError('help без аргументов')
                print_help()

            elif command == 'exit':
                if params:
                    raise ValueError('exit без аргументов')
                print('Завершение работы.')
                break

            else:
                print(
                    f'Функции {command} нет. Попробуйте снова.'
                )

        except FileExistsError as error:
            print(f'Ошибка: {error}')
        except KeyError as error:
            print(f'Ошибка: {error.args[0]}')
        except ValueError as error:
            print(
                f'Некорректное значение: {error}. '
                'Попробуйте снова.'
            )
        except OSError as error:
            print(f'Ошибка при работе с файлом: {error}')