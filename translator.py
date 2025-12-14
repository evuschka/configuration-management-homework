from parser import ConfigParser


class TomlTranslator:
    """Транслятор в формат TOML."""
    
    def __init__(self):
        """Инициализация транслятора."""
        self.parser = ConfigParser()
        self.parser.build(debug=False, write_tables=False)
        self.output_lines = []
        self.table_counter = 0
    
    def translate(self, input_text):
        """
        Трансляция входного текста в TOML.
        
        Args:
            input_text: Текст на учебном конфигурационном языке
            
        Returns:
            Кортеж (toml_output, errors)
        """
        self.output_lines = []
        self.table_counter = 0
        
        # Разбор входного текста
        result = self.parser.parse(input_text)
        errors = self.parser.get_errors()
        
        if errors:
            return None, errors
        
        # Генерация TOML
        constants = self.parser.get_constants()
        
        # Выводим все константы
        for name, value in constants.items():
            toml_value = self._value_to_toml(value)
            self.output_lines.append(f"{name} = {toml_value}")
        
        # Обрабатываем остальные выражения (таблицы верхнего уровня)
        if result:
            for item in result:
                if item is not None and not isinstance(item, tuple):
                    continue
                if item is not None and item[0] != 'const_decl':
                    toml_value = self._value_to_toml(item)
                    if item[0] == 'table':
                        # Таблица верхнего уровня уже обработана
                        pass
        
        return '\n'.join(self.output_lines), []
    
    def _value_to_toml(self, value, indent=0):
        """
        Преобразование значения в TOML формат.
        
        Args:
            value: Значение для преобразования
            indent: Уровень отступа
            
        Returns:
            Строка в формате TOML
        """
        if isinstance(value, int):
            return str(value)
        
        if isinstance(value, tuple):
            if value[0] == 'table':
                return self._table_to_toml(value[1], indent)
            elif value[0] == 'const_ref':
                # Вычисляем значение константы
                ref_value = value[2]
                if ref_value is not None:
                    return self._value_to_toml(ref_value, indent)
                else:
                    return '"undefined"'
        
        return str(value)
    
    def _table_to_toml(self, items, indent=0):
        """
        Преобразование таблицы в TOML формат.
        
        Args:
            items: Список элементов таблицы
            indent: Уровень отступа
            
        Returns:
            Строка в формате TOML
        """
        if not items:
            return "{}"
        
        # Для инлайн-таблиц
        parts = []
        for name, value in items:
            toml_value = self._value_to_toml(value, indent + 1)
            parts.append(f"{name} = {toml_value}")
        
        return "{ " + ", ".join(parts) + " }"
    
    def translate_to_sections(self, input_text):
        """
        Трансляция входного текста в TOML с секциями.
        
        Args:
            input_text: Текст на учебном конфигурационном языке
            
        Returns:
            Кортеж (toml_output, errors)
        """
        self.output_lines = []
        self.table_counter = 0
        
        # Разбор входного текста
        result = self.parser.parse(input_text)
        errors = self.parser.get_errors()
        
        if errors:
            return None, errors
        
        # Генерация TOML с секциями
        constants = self.parser.get_constants()
        
        # Выводим простые константы
        simple_constants = []
        table_constants = []
        
        for name, value in constants.items():
            if isinstance(value, tuple) and value[0] == 'table':
                table_constants.append((name, value))
            else:
                simple_constants.append((name, value))
        
        # Выводим простые константы
        for name, value in simple_constants:
            toml_value = self._value_to_toml(value)
            self.output_lines.append(f"{name} = {toml_value}")
        
        # Выводим таблицы как секции
        for name, value in table_constants:
            self.output_lines.append("")
            self.output_lines.append(f"[{name}]")
            if value[0] == 'table':
                for item_name, item_value in value[1]:
                    toml_value = self._value_to_toml(item_value)
                    self.output_lines.append(f"{item_name} = {toml_value}")
        
        return '\n'.join(self.output_lines), []


# Функция для тестирования транслятора
def test_translator():
    """Тестирование транслятора."""
    translator = TomlTranslator()
    
    test_input = """
    // Конфигурация сервера
    port: 0b10000000;
    maxconn: 0b1111;
    
    server: table([
        port = .(port).,
        connections = .(maxconn).,
        timeout = 0b1100100
    ]);
    """
    
    toml_output, errors = translator.translate_to_sections(test_input)
    
    if errors:
        print("Ошибки:")
        for error in errors:
            print(f"  {error}")
    else:
        print("TOML вывод:")
        print(toml_output)


if __name__ == '__main__':
    test_translator()
