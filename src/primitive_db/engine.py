import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.constants import ID_COLUMN, META_FILE
from primitive_db.core import (
    create_table,
    drop_table,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.parser import parse_insert, parse_set, parse_update, parse_where
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


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
    print(
        "<command> insert into <таблица> "
        "values (<значения>) - добавить запись"
    )
    print(
        "<command> select from <имя_таблицы> "
        "- показать все записи"
    )
    print(
        "<command> select from <таблица> "
        "where <столбец> = <значение> - поиск по условию"
    )
    print(
        "<command> update <таблица> set <столбец> = <значение> "
        "where <столбец> = <значение> - обновить записи"
    )


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

            elif command == 'insert':
                table_name, values = parse_insert(user_input)

                data = insert(metadata, table_name, values)

                save_table_data(table_name, data)

                new_id = data[-1][ID_COLUMN]

                print(
                    f'Запись с ID={new_id} успешно добавлена '
                    f'в таблицу "{table_name}".'
                )

            elif command == 'select':
                parts = user_input.strip().split(maxsplit=4)

                if len(parts) not in (3, 5) or parts[:2] != [
                    'select',
                    'from',
                ]:
                    raise ValueError(
                        'Ожидается: select from <таблица> '
                        '[where <столбец> = <значение>]'
                    )

                table_name = parts[2]

                if table_name not in metadata:
                    raise KeyError(
                        f'Таблица "{table_name}" не существует.'
                    )

                where_clause = None

                if len(parts) == 5:
                    if parts[3] != 'where':
                        raise ValueError('Ожидается ключевое слово where.')

                    where_clause = parse_where(
                        parts[4],
                        metadata[table_name],
                    )

                table_data = load_table_data(table_name)
                records = select(table_data, where_clause)

                table = PrettyTable()
                table.field_names = list(metadata[table_name])

                for record in records:
                    table.add_row(
                        [
                            record[column]
                            for column in table.field_names
                        ]
                    )

                print(table)

            elif command == 'update':
                table_name, set_text, where_text = parse_update(
                    user_input
                )

                if table_name not in metadata:
                    raise KeyError(
                        f'Таблица "{table_name}" не существует.'
                    )

                schema = metadata[table_name]

                set_clause = parse_set(set_text, schema)
                where_clause = parse_where(where_text, schema)

                table_data = load_table_data(table_name)

                matching_records = select(table_data, where_clause)
                record_ids = [
                    record[ID_COLUMN] for record in matching_records
                ]

                if not record_ids:
                    print('Записи по условию WHERE не найдены.')
                    continue

                updated_data = update(
                    table_data,
                    set_clause,
                    where_clause,
                )

                save_table_data(table_name, updated_data)

                for record_id in record_ids:
                    print(
                        f'Запись с ID={record_id} в таблице '
                        f'"{table_name}" успешно обновлена.'
                    )

            else:
                print(
                    f'Функции {command} нет. Попробуйте снова.'
                )

        except FileExistsError as error:
            print(f'Ошибка: {error}')
        except KeyError as error:
            print(f'Ошибка: {error.args[0]}')
        except ValueError as error:
            message = str(error).rstrip(".")
            print(f"Некорректное значение: {message}. Попробуйте снова.")
        except OSError as error:
            print(f'Ошибка при работе с файлом: {error}')