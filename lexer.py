import ply.lex as lex


class ConfigLexer:
    """Лексер для учебного конфигурационного языка."""
    
    # Список токенов
    tokens = (
        'BINARY_NUMBER',    # Двоичное число 0b... или 0B...
        'NAME',             # Имя [a-z]+
        'TABLE',            # Ключевое слово table
        'LPAREN',           # (
        'RPAREN',           # )
        'LBRACKET',         # [
        'RBRACKET',         # ]
        'EQUALS',           # =
        'COMMA',            # ,
        'COLON',            # :
        'SEMICOLON',        # ;
        'DOT',              # .
        'COMMENT',          # Комментарий (для пропуска)
    )
    
    # Игнорируемые символы (пробелы и табуляция)
    t_ignore = ' \t'
    
    # Простые токены
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_EQUALS = r'='
    t_COMMA = r','
    t_COLON = r':'
    t_SEMICOLON = r';'
    t_DOT = r'\.'
    
    def __init__(self):
        """Инициализация лексера."""
        self.lexer = None
        self.errors = []
    
    def t_COMMENT(self, t):
        r'//.*'
        pass  # Комментарии игнорируются
    
    def t_BINARY_NUMBER(self, t):
        r'0[bB][01]+'
        # Преобразуем двоичное число в десятичное
        t.value = int(t.value, 2)
        return t
    
    def t_TABLE(self, t):
        r'table'
        return t
    
    def t_NAME(self, t):
        r'[a-z]+'
        # Проверяем, не является ли это ключевым словом table
        if t.value == 'table':
            t.type = 'TABLE'
        return t
    
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
    def t_error(self, t):
        """Обработка ошибок лексического анализа."""
        error_msg = f"Недопустимый символ '{t.value[0]}' в строке {t.lineno}"
        self.errors.append(error_msg)
        t.lexer.skip(1)
    
    def build(self, **kwargs):
        """Построение лексера."""
        self.lexer = lex.lex(module=self, **kwargs)
        return self.lexer
    
    def input(self, data):
        """Передача входных данных лексеру."""
        self.errors = []
        self.lexer.input(data)
    
    def token(self):
        """Получение следующего токена."""
        return self.lexer.token()
    
    def get_tokens(self, data):
        """Получение списка всех токенов."""
        self.input(data)
        tokens = []
        while True:
            tok = self.token()
            if tok is None:
                break
            tokens.append(tok)
        return tokens


# Функция для тестирования лексера
def test_lexer():
    """Тестирование лексера."""
    lexer = ConfigLexer()
    lexer.build()
    
    test_input = """
    // Это комментарий
    myvar: 0b1010;
    table([
        name = 0b11,
        value = 0b100
    ])
    .(myvar).
    """
    
    tokens = lexer.get_tokens(test_input)
    for tok in tokens:
        print(tok)


if __name__ == '__main__':
    test_lexer()
