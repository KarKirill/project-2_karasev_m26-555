import json


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