from primitive_db.constants import ID_COLUMN, ID_TYPE, VALID_TYPES


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