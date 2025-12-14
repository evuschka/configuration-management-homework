
import pytest
from lexer import ConfigLexer
from parser import ConfigParser
from translator import TomlTranslator


class TestLexer:
    """Тесты лексического анализатора."""
    
    def setup_method(self):
        """Настройка для каждого теста."""
        self.lexer = ConfigLexer()
        self.lexer.build()
    
    def test_binary_number(self):
        """Тест распознавания двоичных чисел."""
        tokens = self.lexer.get_tokens("0b1010")
        assert len(tokens) == 1
        assert tokens[0].type == 'BINARY_NUMBER'
        assert tokens[0].value == 10  # 0b1010 = 10
    
    def test_binary_number_uppercase(self):
        """Тест распознавания двоичных чисел с большой B."""
        tokens = self.lexer.get_tokens("0B1111")
        assert len(tokens) == 1
        assert tokens[0].type == 'BINARY_NUMBER'
        assert tokens[0].value == 15  # 0B1111 = 15
    
    def test_name(self):
        """Тест распознавания имен."""
        tokens = self.lexer.get_tokens("myvar")
        assert len(tokens) == 1
        assert tokens[0].type == 'NAME'
        assert tokens[0].value == 'myvar'
    
    def test_table_keyword(self):
        """Тест распознавания ключевого слова table."""
        tokens = self.lexer.get_tokens("table")
        assert len(tokens) == 1
        assert tokens[0].type == 'TABLE'
    
    def test_comment(self):
        """Тест игнорирования комментариев."""
        tokens = self.lexer.get_tokens("// это комментарий\nmyvar")
        assert len(tokens) == 1
        assert tokens[0].type == 'NAME'
    
    def test_all_tokens(self):
        """Тест всех типов токенов."""
        input_text = "name: 0b101; table([ x = 0b1 ]) .(name)."
        tokens = self.lexer.get_tokens(input_text)
        token_types = [t.type for t in tokens]
        
        expected = [
            'NAME', 'COLON', 'BINARY_NUMBER', 'SEMICOLON',
            'TABLE', 'LPAREN', 'LBRACKET', 'NAME', 'EQUALS', 'BINARY_NUMBER', 'RBRACKET', 'RPAREN',
            'DOT', 'LPAREN', 'NAME', 'RPAREN', 'DOT'
        ]
        assert token_types == expected
    
    def test_invalid_character(self):
        """Тест обработки недопустимых символов."""
        tokens = self.lexer.get_tokens("@invalid")
        assert len(self.lexer.errors) > 0


class TestParser:
    """Тесты синтаксического анализатора."""
    
    def setup_method(self):
        """Настройка для каждого теста."""
        self.parser = ConfigParser()
        self.parser.build(debug=False, write_tables=False)
    
    def test_const_declaration(self):
        """Тест объявления константы."""
        result = self.parser.parse("myvar: 0b1010;")
        assert 'myvar' in self.parser.get_constants()
        assert self.parser.get_constants()['myvar'] == 10
    
    def test_const_reference(self):
        """Тест вычисления константы."""
        result = self.parser.parse("port: 0b1000; .(port).")
        assert len(self.parser.get_errors()) == 0
        constants = self.parser.get_constants()
        assert constants['port'] == 8
    
    def test_simple_table(self):
        """Тест простого словаря."""
        result = self.parser.parse("table([ name = 0b1, value = 0b10 ])")
        assert len(self.parser.get_errors()) == 0
    
    def test_empty_table(self):
        """Тест пустого словаря."""
        result = self.parser.parse("table([])")
        assert len(self.parser.get_errors()) == 0
    
    def test_table_with_const(self):
        """Тест словаря с константой."""
        input_text = """
        port: 0b10000000;
        table([
            serverport = .(port).
        ])
        """
        result = self.parser.parse(input_text)
        assert len(self.parser.get_errors()) == 0
    
    def test_nested_table(self):
        """Тест вложенных словарей."""
        input_text = """
        table([
            outer = table([
                inner = 0b1
            ])
        ])
        """
        result = self.parser.parse(input_text)
        assert len(self.parser.get_errors()) == 0
    
    def test_unknown_constant(self):
        """Тест ошибки неизвестной константы."""
        result = self.parser.parse(".(unknown).")
        errors = self.parser.get_errors()
        assert len(errors) > 0
        assert "Неизвестная константа" in errors[0]
    
    def test_syntax_error(self):
        """Тест синтаксической ошибки."""
        result = self.parser.parse("invalid syntax @#$")
        errors = self.parser.get_errors()
        assert len(errors) > 0
    
    def test_multiple_constants(self):
        """Тест множественных констант."""
        input_text = """
        a: 0b1;
        b: 0b10;
        c: 0b11;
        """
        result = self.parser.parse(input_text)
        constants = self.parser.get_constants()
        assert constants['a'] == 1
        assert constants['b'] == 2
        assert constants['c'] == 3
    
    def test_comments_handling(self):
        """Тест обработки комментариев."""
        input_text = """
        // Это комментарий
        port: 0b1000; // Комментарий после объявления
        // Еще один комментарий
        """
        result = self.parser.parse(input_text)
        assert len(self.parser.get_errors()) == 0
        assert self.parser.get_constants()['port'] == 8


class TestTranslator:
    """Тесты транслятора в TOML."""
    
    def setup_method(self):
        """Настройка для каждого теста."""
        self.translator = TomlTranslator()
    
    def test_simple_constant(self):
        """Тест трансляции простой константы."""
        toml, errors = self.translator.translate("port: 0b1000;")
        assert len(errors) == 0
        assert "port = 8" in toml
    
    def test_simple_table(self):
        """Тест трансляции простого словаря."""
        input_text = "config: table([ port = 0b1000 ]);"
        toml, errors = self.translator.translate(input_text)
        assert len(errors) == 0
        assert "config" in toml
        assert "port = 8" in toml
    
    def test_const_in_table(self):
        """Тест трансляции константы в словаре."""
        input_text = """
        port: 0b1000;
        config: table([ serverport = .(port). ]);
        """
        toml, errors = self.translator.translate(input_text)
        assert len(errors) == 0
        assert "port = 8" in toml
    
    def test_nested_tables(self):
        """Тест трансляции вложенных словарей."""
        input_text = """
        config: table([
            server = table([
                port = 0b1000
            ])
        ]);
        """
        toml, errors = self.translator.translate(input_text)
        assert len(errors) == 0
    
    def test_sections_mode(self):
        """Тест режима с секциями TOML."""
        input_text = """
        server: table([
            port = 0b1000,
            timeout = 0b1100100
        ]);
        """
        toml, errors = self.translator.translate_to_sections(input_text)
        assert len(errors) == 0
        assert "[server]" in toml
    
    def test_error_propagation(self):
        """Тест передачи ошибок."""
        input_text = ".(unknown)."
        toml, errors = self.translator.translate(input_text)
        assert len(errors) > 0
    
    def test_multiple_tables(self):
        """Тест множественных таблиц."""
        input_text = """
        db: table([ port = 0b1011101110 ]);
        cache: table([ size = 0b10000000000 ]);
        """
        toml, errors = self.translator.translate_to_sections(input_text)
        assert len(errors) == 0
        assert "[db]" in toml
        assert "[cache]" in toml
    
    def test_complex_config(self):
        """Тест сложной конфигурации."""
        input_text = """
        // Базовые настройки
        defaultport: 0b10000000;
        maxconn: 0b1111111111;
        
        // Конфигурация сервера
        server: table([
            port = .(defaultport).,
            connections = .(maxconn).,
            settings = table([
                timeout = 0b1100100,
                retries = 0b11
            ])
        ]);
        """
        toml, errors = self.translator.translate_to_sections(input_text)
        assert len(errors) == 0
        assert "defaultport" in toml
        assert "maxconn" in toml


class TestEdgeCases:
    """Тесты граничных случаев."""
    
    def setup_method(self):
        """Настройка для каждого теста."""
        self.parser = ConfigParser()
        self.parser.build(debug=False, write_tables=False)
        self.translator = TomlTranslator()
    
    def test_empty_input(self):
        """Тест пустого входа."""
        result = self.parser.parse("")
        assert len(self.parser.get_errors()) == 0
    
    def test_only_comments(self):
        """Тест только комментариев."""
        input_text = """
        // Комментарий 1
        // Комментарий 2
        // Комментарий 3
        """
        result = self.parser.parse(input_text)
        assert len(self.parser.get_errors()) == 0
    
    def test_binary_zero(self):
        """Тест двоичного нуля."""
        result = self.parser.parse("zero: 0b0;")
        assert self.parser.get_constants()['zero'] == 0
    
    def test_binary_one(self):
        """Тест двоичной единицы."""
        result = self.parser.parse("one: 0b1;")
        assert self.parser.get_constants()['one'] == 1
    
    def test_large_binary_number(self):
        """Тест большого двоичного числа."""
        result = self.parser.parse("large: 0b11111111111111111111;")
        assert self.parser.get_constants()['large'] == 1048575
    
    def test_const_used_before_definition(self):
        """Тест использования константы до объявления."""
        input_text = ".(port). port: 0b1000;"
        result = self.parser.parse(input_text)
        errors = self.parser.get_errors()
        assert len(errors) > 0
    
    def test_deeply_nested_tables(self):
        """Тест глубоко вложенных таблиц."""
        input_text = """
        level: table([
            a = table([
                b = table([
                    c = 0b111
                ])
            ])
        ]);
        """
        result = self.parser.parse(input_text)
        assert len(self.parser.get_errors()) == 0


class TestRealWorldConfigs:
    """Тесты реальных конфигураций."""
    
    def setup_method(self):
        """Настройка для каждого теста."""
        self.translator = TomlTranslator()
    
    def test_server_config(self):
        """Тест конфигурации сервера."""
        input_text = """
        // Конфигурация веб-сервера
        port: 0b10000000;           // Порт 128
        maxclients: 0b1111111111;   // Максимум клиентов 1023
        timeout: 0b111100;          // Таймаут 60
        
        server: table([
            listenport = .(port).,
            maxconnections = .(maxclients).,
            connectiontimeout = .(timeout).,
            settings = table([
                keepalive = 0b1,
                compression = 0b1
            ])
        ]);
        """
        toml, errors = self.translator.translate_to_sections(input_text)
        assert len(errors) == 0
        assert "port = 128" in toml
    
    def test_database_config(self):
        """Тест конфигурации базы данных."""
        input_text = """
        // Конфигурация базы данных
        dbport: 0b1010110111110;    // Порт 5566
        poolsize: 0b1010;           // Размер пула 10
        
        database: table([
            port = .(dbport).,
            pool = .(poolsize).,
            options = table([
                readonly = 0b0,
                cache = 0b1
            ])
        ]);
        """
        toml, errors = self.translator.translate_to_sections(input_text)
        assert len(errors) == 0


# Запуск тестов
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
