from primitive_db.constants import ID_COLUMN, ID_TYPE, VALID_TYPES
from primitive_db.utils import load_table_data


def create_table(metadata, table_name, columns):
    '''Создаёт таблицу с указанными столбцами.'''
    if not table_name.isidentifier():
        raise ValueError(f'недопустимое имя таблицы: {table_name}')

    if table_name in metadata:
        raise FileExistsError(
            f'Таблица "{table_name}" уже существует.'
        )

    if not columns:
        raise ValueError('необходимо указать столбцы')

    schema = {ID_COLUMN: ID_TYPE}

    for column in columns:
        if column.count(':') != 1:
            raise ValueError(column)

        column_name, column_type = column.split(':')

        if not column_name.isidentifier():
            raise ValueError(column_name)

        if column_name in schema:
            raise ValueError(
                f'повторяющийся или зарезервированный столбец: '
                f'{column_name}'
            )

        if column_type not in VALID_TYPES:
            raise ValueError(column_type)

        schema[column_name] = column_type

    metadata[table_name] = schema
    return metadata


def drop_table(metadata, table_name):
    '''Удаляет таблицу из метаданных.'''
    if table_name not in metadata:
        raise KeyError(
            f'Таблица "{table_name}" не существует.'
        )

    del metadata[table_name]
    return metadata


def list_tables(metadata):
    '''Возвращает список существующих таблиц.'''
    return list(metadata)



def insert(metadata: dict, table_name: str, values: list,) -> list[dict]:
    '''Добавляет запись в таблицу с проверкой типов данных.'''
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')

    schema = metadata[table_name]
    column_names = [
        name for name in schema if name != ID_COLUMN
    ]

    if len(values) != len(column_names):
        raise ValueError(
            'Количество значений не соответствует '
            'количеству столбцов.'
        )

    record = {}

    for column_name, value in zip(column_names, values):
        expected_type = schema[column_name]

        if type(value).__name__ != expected_type:
            raise ValueError(
                f'Некорректный тип для столбца '
                f'"{column_name}". Ожидается {expected_type}.'
            )

        record[column_name] = value

    data = load_table_data(table_name)

    new_id = max(
        (row[ID_COLUMN] for row in data),
        default=0,
    ) + 1

    record = {ID_COLUMN: new_id, **record}
    data.append(record)

    return data



def select(
    table_data: list[dict],
    where_clause: dict | None = None,
) -> list[dict]:
    '''Возвращает записи таблицы с учётом условия фильтрации.'''
    if where_clause is None:
        return table_data

    return [
        record
        for record in table_data
        if all(
            record.get(column) == value
            for column, value in where_clause.items()
        )
    ]
