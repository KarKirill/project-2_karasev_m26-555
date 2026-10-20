"""Консольный интерфейс примитивной базы данных."""

import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.constants import ID_COLUMN, META_FILE
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    get_table_info,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from primitive_db.parser import (
    parse_delete,
    parse_insert,
    parse_set,
    parse_update,
    parse_where,
)
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def welcome() -> None:
    """Выводит приветствие из начальной версии проекта."""
    help_text = """
<command> exit - выйти из программы
<command> help - справочная информация
"""

    print('Первая попытка запустить проект!')
    print('\n***')
    print(help_text)

    while True:
        command = prompt.string(prompt='Введите команду: ').strip().lower()

        match command:
            case 'help':
                print(help_text)
            case 'exit':
                print('Выход из программы.')
                break
            case _:
                print(f'Неизвестная команда: {command}')


def print_help() -> None:
    """Выводит справку по командам."""
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
        '<command> insert into <таблица> '
        'values (<значения>) - добавить запись'
    )
    print(
        '<command> select from <имя_таблицы> '
        '- показать все записи'
    )
    print(
        '<command> select from <таблица> '
        'where <столбец> = <значение> - поиск по условию'
    )
    print(
        '<command> update <таблица> set <столбец> = <значение> '
        'where <столбец> = <значение> - обновить записи'
    )
    print(
        '<command> delete from <таблица> '
        'where <столбец> = <значение> - удалить записи'
    )
    print(
        '<command> info <имя_таблицы> '
        '- информация о таблице'
    )


@confirm_action("удалить таблицу")
def confirmed_drop_table(metadata: dict, table_name: str) -> None:
    '''Удаляет таблицу и её данные после подтверждения.'''
    drop_table(metadata, table_name)
    delete_table_data(table_name)
    save_metadata(META_FILE, metadata)
    get_cached_records.clear_cache()

    print(f'Таблица "{table_name}" успешно удалена.')


@confirm_action("удалить записи")
def confirmed_delete_records(
    table_name: str,
    table_data: list[dict],
    where_clause: dict,
    deleted_ids: list[int],
) -> None:
    '''Удаляет записи после подтверждения пользователя.'''
    updated_data = delete(table_data, where_clause)
    save_table_data(table_name, updated_data)
    get_cached_records.clear_cache()

    for record_id in deleted_ids:
        print(
            f'Запись с ID={record_id} успешно удалена '
            f'из таблицы "{table_name}".'
        )


@log_time
def execute_insert(metadata: dict, user_input: str) -> None:
    '''Добавляет запись и сохраняет изменения в JSON.'''
    table_name, values = parse_insert(user_input)

    data = insert(metadata, table_name, values)
    save_table_data(table_name, data)
    get_cached_records.clear_cache()

    new_id = data[-1][ID_COLUMN]

    print(
        f'Запись с ID={new_id} успешно добавлена '
        f'в таблицу "{table_name}".'
    )


@create_cacher()
def get_cached_records(
    table_name: str,
    where_clause: dict | None = None,
) -> list[dict]:
    '''Возвращает записи таблицы с кэшированием результата.'''

    table_data = load_table_data(table_name)
    return select(table_data, where_clause)


@log_time
def execute_select(metadata: dict, user_input: str) -> None:
    '''Выполняет SELECT и выводит результаты в таблицу.'''
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

    records = get_cached_records(table_name, where_clause)

    table = PrettyTable()
    table.field_names = list(metadata[table_name])

    for record in records:
        table.add_row(
            [record[column] for column in table.field_names]
        )

    print(table)


def run() -> None:
    '''Запускает основной цикл ввода команд.'''
    print_help()

    while True:
        user_input = prompt.string('\nВведите команду: ')

        if execute_command(user_input) is False:
            break


@handle_db_errors
def execute_command(user_input: str) -> bool:
    '''Выполняет одну команду базы данных; False означает выход.'''
    metadata = load_metadata(META_FILE)
    args = shlex.split(user_input)

    if not args:
        return True

    command, *params = args

    if command == 'create_table':
        if len(params) < 2:
            raise ValueError('укажите имя таблицы и столбцы')

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
            raise ValueError('Укажите имя таблицы.')

        table_name = params[0]

        if table_name not in metadata:
            raise KeyError(f'Таблица "{table_name}" не существует.')

        confirmed_drop_table(metadata, table_name)

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
        return False

    elif command == 'insert':
        execute_insert(metadata, user_input)

    elif command == 'select':
        execute_select(metadata, user_input)

    elif command == 'update':
        table_name, set_text, where_text = parse_update(user_input)
        if table_name not in metadata:
            raise KeyError(f'Таблица "{table_name}" не существует.')

        schema = metadata[table_name]
        set_clause = parse_set(set_text, schema)
        where_clause = parse_where(where_text, schema)

        table_data = load_table_data(table_name)
        matching_records = select(table_data, where_clause)
        record_ids = [record[ID_COLUMN] for record in matching_records]

        if not record_ids:
            print('Записи по условию WHERE не найдены.')
            return True

        updated_data = update(table_data, set_clause, where_clause)
        save_table_data(table_name, updated_data)
        get_cached_records.clear_cache()

        for record_id in record_ids:
            print(
                f'Запись с ID={record_id} в таблице '
                f'"{table_name}" успешно обновлена.'
            )

    elif command == "delete":
        table_name, where_text = parse_delete(user_input)

        if table_name not in metadata:
            raise KeyError(
                f'Таблица "{table_name}" не существует.'
            )

        schema = metadata[table_name]
        where_clause = parse_where(where_text, schema)

        table_data = load_table_data(table_name)
        matching_records = select(table_data, where_clause)

        if not matching_records:
            print("Записи по условию WHERE не найдены.")
            return True

        deleted_ids = [
            record[ID_COLUMN] for record in matching_records
        ]

        confirmed_delete_records(
            table_name,
            table_data,
            where_clause,
            deleted_ids,
        )

    elif command == 'info':
        if len(params) != 1:
            raise ValueError('Ожидается: info <имя_таблицы>')

        table_name = params[0]
        schema = get_table_info(metadata, table_name)
        table_data = load_table_data(table_name)
        columns = ', '.join(
            f'{name}:{column_type}'
            for name, column_type in schema.items()
        )

        print(f'Таблица: {table_name}')
        print(f'Столбцы: {columns}')
        print(f'Количество записей: {len(table_data)}')

    else:
        print(f'Функции {command} нет. Попробуйте снова.')

    return True