"""
抽象语法树节点定义
"""
from dataclasses import dataclass
from typing import List

@dataclass
class ASTNode:
    """AST基类"""
    pass

@dataclass
class NumberNode(ASTNode):
    """数字节点"""
    value: float

@dataclass
class StringNode(ASTNode):
    """字符串节点"""
    value: str

@dataclass
class VariableNode(ASTNode):
    """变量节点"""
    name: str

@dataclass
class BinOpNode(ASTNode):
    """二元运算节点"""
    left: ASTNode
    op: str
    right: ASTNode

@dataclass
class UnaryOpNode(ASTNode):
    """一元运算节点"""
    op: str
    operand: ASTNode

@dataclass
class FunctionNode(ASTNode):
    """函数调用节点"""
    name: str
    args: List[ASTNode]
