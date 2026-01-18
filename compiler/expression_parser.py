"""
表达式解析器 - 递归下降解析
"""
from .lexer import Token, TokenType
from .ast_nodes import *

class ParseError(Exception):
    """解析错误"""
    pass

class ExpressionParser:
    """递归下降表达式解析器"""

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        """解析表达式"""
        return self._parse_or()

    def _current(self):
        """获取当前token"""
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[self.pos]

    def _peek(self, offset=1):
        """向前看"""
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[pos]

    def _consume(self):
        """消耗当前token"""
        token = self._current()
        self.pos += 1
        return token

    def _match(self, token_type):
        """检查当前token类型"""
        return self._current().type == token_type

    def _match_value(self, token_type, value):
        """检查当前token类型和值"""
        return self._current().type == token_type and self._current().value == value

    def _expect(self, token_type):
        """期望特定类型的token"""
        if not self._match(token_type):
            raise ParseError(f"期望 {token_type}，但得到 {self._current().type}")
        return self._consume()

    # 运算符优先级（从低到高）：
    # 或 → 且 → 比较 → 加减 → 乘除 → 一元 → 括号/原子

    def _parse_or(self):
        """解析 或 运算"""
        left = self._parse_and()
        while self._match_value(TokenType.LOGIC, '或') or self._match_value(TokenType.LOGIC, 'or'):
            op = self._consume().value
            right = self._parse_and()
            left = BinOpNode(left, op, right)
        return left

    def _parse_and(self):
        """解析 且 运算"""
        left = self._parse_comparison()
        while self._match_value(TokenType.LOGIC, '且') or self._match_value(TokenType.LOGIC, 'and'):
            op = self._consume().value
            right = self._parse_comparison()
            left = BinOpNode(left, op, right)
        return left

    def _parse_comparison(self):
        """解析比较运算"""
        left = self._parse_add_sub()
        while self._match(TokenType.OPERATOR) and self._current().value in ['>', '<', '>=', '<=', '=', '≠']:
            op = self._consume().value
            right = self._parse_add_sub()
            left = BinOpNode(left, op, right)
        return left

    def _parse_add_sub(self):
        """解析加减运算"""
        left = self._parse_mul_div()
        while self._match(TokenType.OPERATOR) and self._current().value in ['+', '-']:
            op = self._consume().value
            right = self._parse_mul_div()
            left = BinOpNode(left, op, right)
        return left

    def _parse_mul_div(self):
        """解析乘除运算"""
        left = self._parse_unary()
        while self._match(TokenType.OPERATOR) and self._current().value in ['*', '/', '%']:
            op = self._consume().value
            right = self._parse_unary()
            left = BinOpNode(left, op, right)
        return left

    def _parse_unary(self):
        """解析一元运算"""
        if self._match_value(TokenType.LOGIC, '非') or self._match_value(TokenType.LOGIC, 'not'):
            op = self._consume().value
            operand = self._parse_unary()
            return UnaryOpNode(op, operand)
        if self._match(TokenType.OPERATOR) and self._current().value == '-':
            op = self._consume().value
            operand = self._parse_unary()
            return UnaryOpNode(op, operand)
        return self._parse_primary()

    def _parse_primary(self):
        """解析原子表达式"""
        # 括号
        if self._match(TokenType.LPAREN):
            self._consume()
            expr = self._parse_or()
            self._expect(TokenType.RPAREN)
            return expr

        # 函数调用
        if self._match(TokenType.FUNCTION):
            return self._parse_function()

        # 数字
        if self._match(TokenType.NUMBER):
            return NumberNode(self._consume().value)

        # 字符串
        if self._match(TokenType.STRING):
            return StringNode(self._consume().value)

        # 变量
        if self._match(TokenType.VARIABLE):
            return VariableNode(self._consume().value)

        raise ParseError(f"意外的token: {self._current()}")

    def _parse_function(self):
        """解析函数调用"""
        name = self._consume().value
        self._expect(TokenType.LPAREN)
        args = []
        if not self._match(TokenType.RPAREN):
            args.append(self._parse_or())
            while self._match(TokenType.COMMA):
                self._consume()
                args.append(self._parse_or())
        self._expect(TokenType.RPAREN)
        return FunctionNode(name, args)
