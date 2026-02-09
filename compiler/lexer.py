"""
词法分析器 - 将字符串转换为Token列表
"""
from enum import Enum
from dataclasses import dataclass

class TokenType(Enum):
    NUMBER = "NUMBER"
    STRING = "STRING"
    VARIABLE = "VARIABLE"
    OPERATOR = "OPERATOR"
    LOGIC = "LOGIC"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    FUNCTION = "FUNCTION"
    COMMA = "COMMA"
    EOF = "EOF"

@dataclass
class Token:
    type: TokenType
    value: any
    pos: int

class Lexer:
    """分词器"""

    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    def tokenize(self):
        """将字符串转换为Token列表"""
        tokens = []
        while self.pos < len(self.text):
            if self._current().isspace():
                self.pos += 1
                continue

            if self._current().isdigit():
                tokens.append(self._read_number())
            elif self._current() in '"\'':
                tokens.append(self._read_string())
            elif self._current() == '~':
                tokens.append(self._read_variable())
            elif self._current() in '+-*/%':
                tokens.append(Token(TokenType.OPERATOR, self._current(), self.pos))
                self.pos += 1
            elif self._current() in '><':
                tokens.append(self._read_comparison())
            elif self._current() == '=':
                # 支持 == 和 = 作为相等运算符（Scratch 使用 =）
                if self._peek() == '=':
                    tokens.append(Token(TokenType.OPERATOR, '==', self.pos))
                    self.pos += 2
                else:
                    tokens.append(Token(TokenType.OPERATOR, '=', self.pos))
                    self.pos += 1
            elif self._current() == '!':
                # 检查是否是 !=
                if self._peek() == '=':
                    tokens.append(Token(TokenType.OPERATOR, '≠', self.pos))
                    self.pos += 2
                else:
                    self.pos += 1  # 跳过单独的 !
            elif self._current() == '≠':
                tokens.append(Token(TokenType.OPERATOR, '≠', self.pos))
                self.pos += 1
            elif self._current() == '(':
                tokens.append(Token(TokenType.LPAREN, '(', self.pos))
                self.pos += 1
            elif self._current() == ')':
                tokens.append(Token(TokenType.RPAREN, ')', self.pos))
                self.pos += 1
            elif self._current() == ',':
                tokens.append(Token(TokenType.COMMA, ',', self.pos))
                self.pos += 1
            elif self._current() == '.':
                # 处理小数点：.5 是有效数字，单独的 . 是错误
                if self._peek().isdigit():
                    tokens.append(self._read_number())
                else:
                    from compiler.exceptions import ParseError
                    raise ParseError(f"无效的字符: '.'", self.pos)
            else:
                tokens.append(self._read_word())

        tokens.append(Token(TokenType.EOF, None, self.pos))
        return tokens

    def _current(self):
        """获取当前字符"""
        if self.pos >= len(self.text):
            return '\0'
        return self.text[self.pos]

    def _peek(self, offset=1):
        """向前看"""
        pos = self.pos + offset
        if pos >= len(self.text):
            return '\0'
        return self.text[pos]

    def _read_number(self):
        """读取数字 - 支持整数、浮点数"""
        from compiler.exceptions import ParseError

        start = self.pos

        # 状态机解析数字，确保格式正确
        has_digit = False
        has_dot = False

        # 读取整数部分
        while self._current().isdigit():
            has_digit = True
            self.pos += 1

        # 读取小数部分（只能有一个小数点）
        if self._current() == '.':
            # 检查后面是否还有另一个小数点（如 1.2.3）
            peek_pos = self.pos + 1
            while peek_pos < len(self.text) and self.text[peek_pos].isdigit():
                peek_pos += 1
            if peek_pos < len(self.text) and self.text[peek_pos] == '.':
                # 发现 1.2.3 这种格式，抛出错误
                raise ParseError(f"无效的数字格式: 多个小数点", start)

            has_dot = True
            self.pos += 1
            # 小数点后必须有数字
            while self._current().isdigit():
                has_digit = True
                self.pos += 1

        # 科学计数法
        if self._current().lower() == 'e':
            self.pos += 1
            if self._current() in '+-':
                self.pos += 1
            # e 后必须有数字
            e_has_digit = False
            while self._current().isdigit():
                e_has_digit = True
                self.pos += 1
            if not e_has_digit:
                raise ParseError(f"科学计数法格式错误: 'e' 后缺少数字", start)

        value_str = self.text[start:self.pos]

        if not has_digit:
            raise ParseError(f"无效的数字格式: '{value_str}'", start)

        # 转换为数值
        try:
            if has_dot or 'e' in value_str.lower():
                return Token(TokenType.NUMBER, float(value_str), start)
            else:
                return Token(TokenType.NUMBER, int(value_str), start)
        except ValueError as e:
            raise ParseError(f"无效的数字格式: '{value_str}' - {e}", start)

    def _read_string(self):
        """读取字符串"""
        start = self.pos
        quote = self._current()
        self.pos += 1
        value = ''
        while self._current() != quote and self._current() != '\0':
            value += self._current()
            self.pos += 1
        if self._current() == quote:
            self.pos += 1
        return Token(TokenType.STRING, value, start)

    def _read_variable(self):
        """读取变量引用 ~变量名"""
        start = self.pos
        self.pos += 1  # 跳过 ~
        name = ''
        while self._current() != '\0' and (self._current().isalnum() or self._current() in '_' or ord(self._current()) > 127):
            name += self._current()
            self.pos += 1
        return Token(TokenType.VARIABLE, name, start)

    def _read_comparison(self):
        """读取比较运算符 > < >= <="""
        start = self.pos
        op = self._current()
        self.pos += 1
        if self._current() == '=':
            op += '='
            self.pos += 1
        return Token(TokenType.OPERATOR, op, start)

    def _read_word(self):
        """读取单词（逻辑运算符或函数名）"""
        start = self.pos
        word = ''
        while self._current() != '\0' and (self._current().isalnum() or self._current() in '_' or ord(self._current()) > 127):
            word += self._current()
            self.pos += 1

        # 逻辑运算符
        if word in ['且', '或', '非', '不是', 'and', 'or', 'not']:
            # 将"不是"映射为"非"
            if word == '不是':
                word = '非'
            return Token(TokenType.LOGIC, word, start)

        # 函数名
        if word in ['四舍五入', 'abs', 'floor', 'ceiling', 'sqrt', 'sin', 'cos', 'tan',
                    'asin', 'acos', 'atan', 'ln', 'log', 'round']:
            return Token(TokenType.FUNCTION, word, start)

        # 其他单词作为字符串处理
        return Token(TokenType.STRING, word, start)
