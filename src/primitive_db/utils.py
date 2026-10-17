import json
import os

from primitive_db.constants import DATA_DIR


def load_metadata(filepath) -> dict:
    '''
    Загружает данные из JSON-файла.
    '''
    
    try:
        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data) -> None:
    '''
    Сохраняет данные в JSON-файл.
    '''

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_table_data(table_name: str) -> list[dict]:
    '''Загружает записи таблицы из JSON-файла.'''
    filepath = os.path.join(DATA_DIR, f'{table_name}.json')

    try:
        with open(filepath, encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: list[dict]) -> None:
    '''Сохраняет записи таблицы в JSON-файл.'''
    os.makedirs(DATA_DIR, exist_ok=True)

    filepath = os.path.join(DATA_DIR, f'{table_name}.json')

    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
