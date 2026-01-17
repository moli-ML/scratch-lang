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
            # 中文关键字 - 事件
            "当绿旗被点击", "当按下", "当角色被点击", "当舞台被点击", "当收到", "当背景换成", "当作为克隆体启动",
            # 中文关键字 - 动作
            "移动", "旋转右", "旋转左", "移到", "面向", "滑行", "碰到边缘就反弹", "将旋转方式设为",
            # 中文关键字 - 外观
            "说", "想", "切换造型到", "下一个造型", "切换背景到", "下一个背景", "将大小设为", "将大小增加",
            "显示", "隐藏", "移至最前层", "移至最后层", "图层增加", "图层减少", "将颜色特效增加", "将颜色特效设为", "清除图形特效",
            # 中文关键字 - 声音
            "播放声音", "停止所有声音", "将音量设为", "将音量增加", "将音调设为", "清除声音特效",
            # 中文关键字 - 控制
            "重复", "重复执行", "如果", "那么", "否则", "结束", "等待", "等待直到", "重复执行直到",
            "停止", "停止全部", "停止此脚本", "停止此角色的其他脚本", "广播", "克隆", "删除此克隆体",
            # 中文关键字 - 侦测
            "询问", "并等待", "计时器归零", "设置拖动模式为",
            # 中文关键字 - 运算
            "四舍五入", "字符串长度",
            # 中文关键字 - 变量和列表
            "设置", "将", "增加", "显示变量", "隐藏变量", "列表", "添加", "删除", "清空", "插入", "替换",
            # 中文关键字 - 画笔
            "清空", "图章", "落笔", "抬笔", "将笔的颜色设为", "将笔的粗细设为", "将笔的粗细增加", "将笔的颜色增加", "将笔的亮度增加",
            # 中文关键字 - 音乐
            "演奏音符", "演奏鼓声", "休止", "将乐器设为", "将节奏设为", "将节奏增加",
            # 中文关键字 - 自定义
            "定义", "不刷新屏幕",
            # 英文关键字
            "when flag clicked", "when", "key pressed", "sprite clicked", "stage clicked", "backdrop switches to", "start as a clone",
            "repeat", "forever", "if", "then", "else", "end", "wait", "until",
            "move", "steps", "turn right", "turn left", "degrees", "go to", "point", "glide", "if on edge, bounce",
            "say", "think", "switch costume to", "next costume", "switch backdrop to", "next backdrop", "show", "hide",
            "play sound", "stop all sounds", "set volume to", "change volume by",
            "broadcast", "clone", "delete this clone", "stop",
            "ask", "and wait", "reset timer",
            "round", "length",
            "set", "change", "by", "add", "delete", "insert", "replace",
            "pen down", "pen up", "stamp", "clear",
            "play note", "play drum", "rest", "set instrument to", "set tempo to", "change tempo by",
            "define", "warp"
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

        # 块注释格式 (简单匹配，不跨行)
        self.highlighting_rules.append((QRegExp("/\\*.*\\*/"), comment_format))

        # 多行字符串格式
        multiline_string_format = QTextCharFormat()
        multiline_string_format.setForeground(QColor("#59C059"))
        self.highlighting_rules.append((QRegExp('""".*"""'), multiline_string_format))

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
        self.highlighting_rules.append((QRegExp("(造型|背景|音效|变量|列表|云变量|costume|backdrop|sound|var|list|cloud):"), resource_format))

        # 扩展导入
        extension_format = QTextCharFormat()
        extension_format.setForeground(QColor("#FF8C1A"))
        extension_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((QRegExp("(导入扩展|import extension):"), extension_format))

        # 代码块标记
        code_block_format = QTextCharFormat()
        code_block_format.setForeground(QColor("#FF6680"))
        code_block_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((QRegExp("^#code#$"), code_block_format))
        self.highlighting_rules.append((QRegExp("^#end#$"), code_block_format))

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