import argparse
import sys
import os

from translator import TomlTranslator


def main():
    """Главная функция программы."""
    # Парсинг аргументов командной строки
    arg_parser = argparse.ArgumentParser(
        description='Транслятор учебного конфигурационного языка в TOML (Вариант №11)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Синтаксис учебного конфигурационного языка:
  - Числа: 0[bB][01]+ (двоичные числа)
  - Словари: table([ имя = значение, ... ])
  - Имена: [a-z]+
  - Объявление константы: имя: значение;
  - Вычисление константы: .(имя).
  - Комментарии: // текст комментария

Примеры:
  python main.py --input examples/server_config.txt
  python main.py -i examples/database_config.txt
        """
    )
    
    arg_parser.add_argument(
        '-i', '--input',
        required=True,
        help='Путь к входному файлу с конфигурацией'
    )
    
    arg_parser.add_argument(
        '-s', '--sections',
        action='store_true',
        help='Использовать секции TOML для таблиц (вместо инлайн-таблиц)'
    )
    
    args = arg_parser.parse_args()
    
    # Проверка существования файла
    if not os.path.exists(args.input):
        print(f"Ошибка: файл '{args.input}' не найден", file=sys.stderr)
        sys.exit(1)
    
    # Чтение входного файла
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            input_text = f.read()
    except IOError as e:
        print(f"Ошибка чтения файла: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Создание транслятора и трансляция
    translator = TomlTranslator()
    
    if args.sections:
        toml_output, errors = translator.translate_to_sections(input_text)
    else:
        toml_output, errors = translator.translate(input_text)
    
    # Вывод результатов
    if errors:
        for error in errors:
            print(f"Ошибка: {error}", file=sys.stderr)
        sys.exit(1)
    else:
        print(toml_output)


if __name__ == '__main__':
    main()
