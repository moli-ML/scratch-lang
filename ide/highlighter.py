"""
语法高亮器 - 支持括号匹配高亮
"""
from typing import List, Tuple, Optional
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter, QTextDocument


class ScratchLangHighlighter(QSyntaxHighlighter):
    """ScratchLang 语法高亮器"""

    # 括号对
    BRACKETS = [('(', ')'), ('[', ']'), ('{', '}')]

    def __init__(self, parent: Optional[QTextDocument] = None) -> None:
        super().__init__(parent)
        self.highlighting_rules: List[Tuple[QRegExp, QTextCharFormat]] = []

        # 关键字格式
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#FF6680"))
        keyword_format.setFontWeight(QFont.Bold)

        keywords = [
            "当绿旗被点击", "当按下", "当收到", "重复", "重复执行", "如果", "那么",
            "否则", "结束", "移动", "旋转右", "旋转左", "移到", "说", "想",
            "等待", "广播", "克隆", "停止", "显示", "隐藏", "切换背景到", "下一个背景",
            "碰到边缘就反弹", "落笔", "抬笔", "设置", "将", "增加", "询问", "并等待"
        ]

        for word in keywords:
            pattern = QRegExp(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, keyword_format))

        # 数字格式
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#855CD6"))
        self.highlighting_rules.append((QRegExp("\\b[0-9]+\\.?[0-9]*\\b"), number_format))

        # 字符串格式
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#59C059"))
        self.highlighting_rules.append((QRegExp('"[^"]*"'), string_format))
        self.highlighting_rules.append((QRegExp("'[^']*'"), string_format))

        # 注释格式
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#888888"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((QRegExp("//[^\n]*"), comment_format))

        # 角色声明
        sprite_format = QTextCharFormat()
        sprite_format.setForeground(QColor("#0FBD8C"))
        sprite_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((QRegExp("^#.*"), sprite_format))

        # 舞台声明
        stage_format = QTextCharFormat()
        stage_format.setForeground(QColor("#4C97FF"))
        stage_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((QRegExp("^@.*"), stage_format))

        # 开始标记
        start_format = QTextCharFormat()
        start_format.setForeground(QColor("#FF8C1A"))
        start_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((QRegExp("^:.*"), start_format))

        # 资源关键字
        resource_format = QTextCharFormat()
        resource_format.setForeground(QColor("#9966FF"))
        resource_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((QRegExp("(造型|背景|音效|变量|列表):"), resource_format))

        # 变量引用 (~变量名)
        variable_format = QTextCharFormat()
        variable_format.setForeground(QColor("#FF8C1A"))
        self.highlighting_rules.append((QRegExp("~\\w+"), variable_format))

        # 括号格式
        self.bracket_format = QTextCharFormat()
        self.bracket_format.setForeground(QColor("#FFD700"))
        self.bracket_format.setFontWeight(QFont.Bold)

    def highlightBlock(self, text: str) -> None:
        """高亮文本块"""
        for pattern, fmt in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, fmt)
                index = expression.indexIn(text, index + length)

        # 高亮括号
        for i, char in enumerate(text):
            for open_b, close_b in self.BRACKETS:
                if char == open_b or char == close_b:
                    self.setFormat(i, 1, self.bracket_format)