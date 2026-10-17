import json
from primitive_db.constants import ID_COLUMN

def parse_insert(user_input: str) -> tuple[str, list]:
    '''Разбирает команду INSERT на имя таблицы и значения.'''
    parts = user_input.strip().split(maxsplit=3)

    if len(parts) != 4 or parts[:2] != ['insert', 'into']:
        raise ValueError(
            'Ожидается: insert into <таблица> values (...)'
        )

    table_name = parts[2]

    keyword, bracket, values_text = parts[3].partition('(')

    if keyword.strip() != 'values' or not bracket:
        raise ValueError('Некорректный формат values.')

    if not values_text.endswith(')'):
        raise ValueError('Отсутствует закрывающая скобка.')

    try:
        values = json.loads(f'[{values_text[:-1]}]')
    except json.JSONDecodeError as error:
        raise ValueError(
            'Некорректные значения. Строки указывайте '
            'в двойных кавычках, bool - как true или false.'
        ) from error

    return table_name, values



def parse_where(
    condition: str,
    schema: dict[str, str],
) -> dict[str, object]:
    '''Разбирает условие WHERE и проверяет тип значения.'''
    column_name, separator, raw_value = condition.partition('=')

    column_name = column_name.strip()
    raw_value = raw_value.strip()

    if not separator or not column_name or not raw_value:
        raise ValueError('Ожидается условие: столбец = значение')

    if column_name not in schema:
        raise ValueError(f'Столбец "{column_name}" не существует.')

    try:
        value = json.loads(raw_value)
    except json.JSONDecodeError as error:
        raise ValueError(
            'Некорректное значение WHERE. '
            'Строки указывайте в двойных кавычках.'
        ) from error

    expected_type = schema[column_name]

    if type(value).__name__ != expected_type:
        raise ValueError(
            f'Некорректный тип для столбца "{column_name}". '
            f'Ожидается {expected_type}.'
        )

    return {column_name: value}



def parse_set(
    condition: str,
    schema: dict[str, str],
) -> dict[str, object]:
    '''Разбирает условие SET и проверяет новое значение.'''
    set_clause = parse_where(condition, schema)

    if ID_COLUMN in set_clause:
        raise ValueError('Столбец ID изменять нельзя.')

    return set_clause



def parse_update(user_input: str) -> tuple[str, str, str]:
    '''Разбирает UPDATE на таблицу, SET и WHERE.'''
    parts = user_input.strip().split(maxsplit=3)

    if (
        len(parts) != 4
        or parts[0] != 'update'
        or parts[2] != 'set'
    ):
        raise ValueError(
            'Ожидается: update <таблица> '
            'set <условие> where <условие>'
        )

    table_name = parts[1]

    set_text, separator, where_text = parts[3].partition(' where ')

    if not separator or not set_text.strip() or not where_text.strip():
        raise ValueError('Для UPDATE необходимо условие WHERE.')

    return table_name, set_text.strip(), where_text.strip()
