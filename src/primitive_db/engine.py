import prompt

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