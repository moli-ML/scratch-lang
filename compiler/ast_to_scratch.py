"""
AST转Scratch JSON转换器
"""
from .ast_nodes import *

class ASTToScratch:
    """将AST转换为Scratch积木JSON"""

    def __init__(self, builder):
        self.builder = builder

    def convert(self, node):
        """
        转换AST节点为Scratch积木
        返回: (block_type, block_id或value)
        - block_type: 1=直接值, 2=shadow block, 3=block
        """
        if isinstance(node, NumberNode):
            # Scratch格式: [1, [4, "数字"]]
            return (1, [4, str(node.value)])

        elif isinstance(node, StringNode):
            # Scratch格式: [1, [10, "字符串"]]
            return (1, [10, node.value])

        elif isinstance(node, VariableNode):
            return self._convert_variable(node)

        elif isinstance(node, BinOpNode):
            return self._convert_binop(node)

        elif isinstance(node, UnaryOpNode):
            return self._convert_unary(node)

        elif isinstance(node, FunctionNode):
            return self._convert_function(node)

        else:
            raise ValueError(f"不支持的AST节点类型: {type(node)}")

    def _convert_variable(self, node):
        """转换变量节点"""
        block_id = self.builder.generate_id()
        self.builder.current_sprite["blocks"][block_id] = {
            "opcode": "data_variable",
            "next": None,
            "parent": None,
            "inputs": {},
            "fields": {"VARIABLE": [node.name, None]},
            "shadow": True,
            "topLevel": False
        }
        return (2, block_id)

    def _convert_binop(self, node):
        """转换二元运算节点"""
        # 映射运算符到Scratch opcode
        op_map = {
            '+': ('operator_add', 'NUM1', 'NUM2'),
            '-': ('operator_subtract', 'NUM1', 'NUM2'),
            '*': ('operator_multiply', 'NUM1', 'NUM2'),
            '/': ('operator_divide', 'NUM1', 'NUM2'),
            '%': ('operator_mod', 'NUM1', 'NUM2'),
            '>': ('operator_gt', 'OPERAND1', 'OPERAND2'),
            '<': ('operator_lt', 'OPERAND1', 'OPERAND2'),
            '=': ('operator_equals', 'OPERAND1', 'OPERAND2'),
            '且': ('operator_and', 'OPERAND1', 'OPERAND2'),
            'and': ('operator_and', 'OPERAND1', 'OPERAND2'),
            '或': ('operator_or', 'OPERAND1', 'OPERAND2'),
            'or': ('operator_or', 'OPERAND1', 'OPERAND2'),
        }

        # 处理 >= 和 <= (转换为 not (a < b) 和 not (a > b))
        if node.op == '>=':
            # a >= b  =>  not (a < b)
            lt_node = BinOpNode(node.left, '<', node.right)
            not_node = UnaryOpNode('非', lt_node)
            return self.convert(not_node)

        if node.op == '<=':
            # a <= b  =>  not (a > b)
            gt_node = BinOpNode(node.left, '>', node.right)
            not_node = UnaryOpNode('非', gt_node)
            return self.convert(not_node)

        if node.op == '≠':
            # a ≠ b  =>  not (a = b)
            eq_node = BinOpNode(node.left, '=', node.right)
            not_node = UnaryOpNode('非', eq_node)
            return self.convert(not_node)

        if node.op not in op_map:
            raise ValueError(f"不支持的运算符: {node.op}")

        opcode, input1, input2 = op_map[node.op]

        # 递归转换左右子树
        left_type, left_value = self.convert(node.left)
        right_type, right_value = self.convert(node.right)

        # 创建运算符积木
        block_id = self.builder.generate_id()
        self.builder.current_sprite["blocks"][block_id] = {
            "opcode": opcode,
            "next": None,
            "parent": None,
            "inputs": {
                input1: [left_type, left_value],
                input2: [right_type, right_value]
            },
            "fields": {},
            "shadow": False,
            "topLevel": False
        }

        return (2, block_id)

    def _convert_unary(self, node):
        """转换一元运算节点"""
        if node.op == '-':
            # 负号: 0 - operand
            zero_node = NumberNode(0)
            sub_node = BinOpNode(zero_node, '-', node.operand)
            return self.convert(sub_node)

        elif node.op in ['非', 'not']:
            # 非运算
            operand_type, operand_value = self.convert(node.operand)

            block_id = self.builder.generate_id()
            self.builder.current_sprite["blocks"][block_id] = {
                "opcode": "operator_not",
                "next": None,
                "parent": None,
                "inputs": {
                    "OPERAND": [operand_type, operand_value]
                },
                "fields": {},
                "shadow": False,
                "topLevel": False
            }
            return (2, block_id)

        else:
            raise ValueError(f"不支持的一元运算符: {node.op}")

    def _convert_function(self, node):
        """转换函数调用节点"""
        # 映射函数名到Scratch opcode
        func_map = {
            '四舍五入': 'operator_round',
            'round': 'operator_round',
            'abs': 'operator_mathop',
            'floor': 'operator_mathop',
            'ceiling': 'operator_mathop',
            'sqrt': 'operator_mathop',
            'sin': 'operator_mathop',
            'cos': 'operator_mathop',
            'tan': 'operator_mathop',
            'asin': 'operator_mathop',
            'acos': 'operator_mathop',
            'atan': 'operator_mathop',
            'ln': 'operator_mathop',
            'log': 'operator_mathop',
        }

        if node.name not in func_map:
            raise ValueError(f"不支持的函数: {node.name}")

        opcode = func_map[node.name]

        if len(node.args) == 0:
            raise ValueError(f"函数 {node.name} 需要参数")

        # 转换参数
        arg_type, arg_value = self.convert(node.args[0])

        block_id = self.builder.generate_id()

        if node.name in ['四舍五入', 'round']:
            # 四舍五入
            self.builder.current_sprite["blocks"][block_id] = {
                "opcode": opcode,
                "next": None,
                "parent": None,
                "inputs": {
                    "NUM": [arg_type, arg_value]
                },
                "fields": {},
                "shadow": False,
                "topLevel": False
            }
        else:
            # 数学运算
            # 映射函数名到Scratch的OPERATOR字段
            operator_map = {
                'abs': 'abs',
                'floor': 'floor',
                'ceiling': 'ceiling',
                'sqrt': 'sqrt',
                'sin': 'sin',
                'cos': 'cos',
                'tan': 'tan',
                'asin': 'asin',
                'acos': 'acos',
                'atan': 'atan',
                'ln': 'ln',
                'log': 'log',
            }
            operator = operator_map.get(node.name, node.name)

            self.builder.current_sprite["blocks"][block_id] = {
                "opcode": opcode,
                "next": None,
                "parent": None,
                "inputs": {
                    "NUM": [arg_type, arg_value]
                },
                "fields": {
                    "OPERATOR": [operator, None]
                },
                "shadow": False,
                "topLevel": False
            }

        return (2, block_id)
