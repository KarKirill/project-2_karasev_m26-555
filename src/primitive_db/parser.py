import json


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
