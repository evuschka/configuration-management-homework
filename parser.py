import ply.yacc as yacc
from lexer import ConfigLexer


class ConfigParser:
    """Парсер для учебного конфигурационного языка."""
    
    def __init__(self):
        """Инициализация парсера."""
        self.lexer = ConfigLexer()
        self.lexer.build()
        self.tokens = self.lexer.tokens
        self.parser = None
        self.errors = []
        self.constants = {}  # Хранилище констант
        self.result = []     # Результат разбора
    
    # Правила грамматики
    
    def p_program(self, p):
        """program : statements"""
        p[0] = p[1]
    
    def p_statements(self, p):
        """statements : statements statement
                      | statement
                      | empty"""
        if len(p) == 3:
            if p[1] is None:
                p[0] = [p[2]] if p[2] is not None else []
            else:
                p[0] = p[1] + ([p[2]] if p[2] is not None else [])
        elif p[1] is not None:
            p[0] = [p[1]]
        else:
            p[0] = []
    
    def p_statement(self, p):
        """statement : const_declaration
                     | value"""
        p[0] = p[1]
    
    def p_const_declaration(self, p):
        """const_declaration : NAME COLON value SEMICOLON"""
        name = p[1]
        value = p[3]
        self.constants[name] = value
        p[0] = ('const_decl', name, value)
    
    def p_value(self, p):
        """value : BINARY_NUMBER
                 | table
                 | const_ref"""
        p[0] = p[1]
    
    def p_table(self, p):
        """table : TABLE LPAREN LBRACKET table_items RBRACKET RPAREN
                 | TABLE LPAREN LBRACKET RBRACKET RPAREN"""
        if len(p) == 7:
            p[0] = ('table', p[4])
        else:
            p[0] = ('table', [])
    
    def p_table_items(self, p):
        """table_items : table_items COMMA table_item
                       | table_item"""
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]
    
    def p_table_item(self, p):
        """table_item : NAME EQUALS value"""
        p[0] = (p[1], p[3])
    
    def p_const_ref(self, p):
        """const_ref : DOT LPAREN NAME RPAREN DOT"""
        name = p[3]
        if name in self.constants:
            p[0] = ('const_ref', name, self.constants[name])
        else:
            error_msg = f"Неизвестная константа: {name}"
            self.errors.append(error_msg)
            p[0] = ('const_ref', name, None)
    
    def p_empty(self, p):
        """empty :"""
        p[0] = None
    
    def p_error(self, p):
        """Обработка синтаксических ошибок."""
        if p:
            error_msg = f"Ошибка синтаксиса в строке {p.lineno}: неожиданный токен '{p.value}'"
            self.errors.append(error_msg)
        else:
            error_msg = "Ошибка синтаксиса: неожиданный конец файла"
            self.errors.append(error_msg)
    
    def build(self, **kwargs):
        """Построение парсера."""
        self.parser = yacc.yacc(module=self, **kwargs)
        return self.parser
    
    def parse(self, data):
        """Разбор входных данных."""
        self.errors = []
        self.constants = {}
        self.lexer.input(data)
        result = self.parser.parse(data, lexer=self.lexer.lexer)
        
        # Добавляем ошибки лексера
        self.errors.extend(self.lexer.errors)
        
        return result
    
    def get_constants(self):
        """Получение словаря констант."""
        return self.constants
    
    def get_errors(self):
        """Получение списка ошибок."""
        return self.errors


# Функция для тестирования парсера
def test_parser():
    """Тестирование парсера."""
    parser = ConfigParser()
    parser.build(debug=False, write_tables=False)
    
    test_input = """
    // Определение констант
    port: 0b10000000;
    maxconn: 0b1111;
    
    // Использование констант в таблице
    table([
        serverport = .(port).,
        connections = .(maxconn).,
        timeout = 0b1100100
    ])
    """
    
    result = parser.parse(test_input)
    print("Результат разбора:", result)
    print("Константы:", parser.get_constants())
    print("Ошибки:", parser.get_errors())


if __name__ == '__main__':
    test_parser()
