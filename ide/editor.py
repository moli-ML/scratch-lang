"""
代码编辑器 - 带行号显示、语法高亮、自动补全、实时语法检查和代码折叠的代码编辑器组件
"""
import re
from typing import TYPE_CHECKING, List, Tuple, Dict, Set
from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QCompleter, QAbstractItemView
from PyQt5.QtCore import Qt, QRect, QSize, QStringListModel, QTimer, pyqtSignal
from PyQt5.QtGui import (QColor, QPainter, QTextFormat, QFont, QPaintEvent,
                         QResizeEvent, QTextCursor, QTextCharFormat, QMouseEvent,
                         QPolygon)
from PyQt5.QtCore import QPoint
from .highlighter import ScratchLangHighlighter

if TYPE_CHECKING:
    from PyQt5.QtCore import QRectF


class FoldingArea(QWidget):
    """代码折叠区域组件"""

    def __init__(self, editor: 'CodeEditor') -> None:
        super().__init__(editor)
        self.editor = editor
        self.setFixedWidth(14)

    def paintEvent(self, event: QPaintEvent) -> None:
        self.editor.foldingAreaPaintEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.editor.foldingAreaMousePressEvent(event)


class LineNumberArea(QWidget):
    """行号显示区域组件"""

    def __init__(self, editor: 'CodeEditor') -> None:
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event: QPaintEvent) -> None:
        self.editor.lineNumberAreaPaintEvent(event)


class CodeEditor(QPlainTextEdit):
    """代码编辑器组件

    支持行号显示、语法高亮和自动补全的代码编辑器。
    """

    # 自动补全关键字列表
    KEYWORDS: List[str] = [
        # 事件
        "当绿旗被点击", "当按下", "键", "当角色被点击", "当舞台被点击",
        "当收到", "当背景换成", "当作为克隆体启动",
        # 动作
        "移动", "步", "旋转右", "旋转左", "度", "移到", "面向", "方向",
        "在", "秒内滑行到", "将x坐标增加", "将x坐标设为", "将y坐标增加", "将y坐标设为",
        "碰到边缘就反弹", "将旋转方式设为",
        # 外观
        "说", "秒", "想", "切换造型到", "下一个造型", "切换背景到", "下一个背景",
        "将大小设为", "将大小增加", "显示", "隐藏", "移至最前层", "移至最后层",
        "图层增加", "图层减少", "清除图形特效",
        # 声音
        "播放声音", "并等待", "停止所有声音", "将音量设为", "将音量增加",
        # 控制
        "等待", "重复", "次", "重复执行", "如果", "那么", "否则", "结束",
        "等待直到", "重复执行直到", "停止", "全部", "此脚本", "克隆", "删除此克隆体",
        "广播",
        # 侦测
        "询问", "计时器归零", "设置拖动模式为",
        # 变量
        "变量:", "列表:", "设置", "为", "将", "增加", "显示变量", "隐藏变量",
        "添加", "到", "删除", "的第", "项", "清空", "插入", "替换",
        # 画笔
        "清空", "图章", "落笔", "抬笔", "将笔的颜色设为", "将笔的粗细设为",
        # 特殊
        "造型:", "背景:", "音效:", "鼠标指针", "随机位置", "边缘", "舞台",
        "空格", "上", "下", "左", "右", "回车", "任意",
    ]

    # 语法错误信号
    syntax_errors_changed = pyqtSignal(list)

    # 可折叠的关键字（开始和结束）
    FOLD_START_KEYWORDS = ['重复执行', '重复', '如果']
    FOLD_END_KEYWORD = '结束'

    def __init__(self) -> None:
        super().__init__()
        self.lineNumberArea = LineNumberArea(self)
        self.foldingArea = FoldingArea(self)
        self.highlighter = ScratchLangHighlighter(self.document())

        # 折叠相关数据
        self.fold_regions: Dict[int, int] = {}  # 起始行 -> 结束行
        self.folded_blocks: Set[int] = set()  # 已折叠的起始行

        # 设置字体
        font = QFont("Consolas", 11)
        self.setFont(font)

        # 连接信号
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.textChanged.connect(self.update_fold_regions)

        self.updateLineNumberAreaWidth(0)

        # 设置自动补全
        self.setup_completer()

        # 设置实时语法检查
        self.syntax_errors: List[Tuple[int, str]] = []
        self.syntax_check_timer = QTimer(self)
        self.syntax_check_timer.setSingleShot(True)
        self.syntax_check_timer.timeout.connect(self.check_syntax)
        self.textChanged.connect(self.schedule_syntax_check)

        # 初始化折叠区域
        self.update_fold_regions()

    def schedule_syntax_check(self) -> None:
        """延迟触发语法检查（避免频繁检查）"""
        self.syntax_check_timer.start(500)  # 500ms 延迟

    def check_syntax(self) -> None:
        """检查语法错误"""
        self.syntax_errors = []
        text = self.toPlainText()
        lines = text.split('\n')

        bracket_stack = []  # 用于检查括号匹配
        control_stack = []  # 用于检查控制结构

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # 跳过空行和注释
            if not stripped or stripped.startswith('//'):
                continue

            # 检查括号匹配
            for i, char in enumerate(stripped):
                if char in '([{':
                    bracket_stack.append((char, line_num))
                elif char in ')]}':
                    if not bracket_stack:
                        self.syntax_errors.append((line_num, f"多余的右括号 '{char}'"))
                    else:
                        open_bracket, _ = bracket_stack.pop()
                        expected = {'(': ')', '[': ']', '{': '}'}[open_bracket]
                        if char != expected:
                            self.syntax_errors.append((line_num, f"括号不匹配，期望 '{expected}' 但得到 '{char}'"))

            # 检查控制结构
            if any(keyword in stripped for keyword in ['重复', '如果', '重复执行']):
                if '那么' in stripped or stripped.startswith('重复执行') or '次' in stripped:
                    control_stack.append((stripped.split()[0] if stripped.split() else '', line_num))

            if stripped in ['结束', 'end', '}']:
                if not control_stack:
                    self.syntax_errors.append((line_num, "多余的 '结束'，没有对应的控制结构"))
                else:
                    control_stack.pop()

            # 检查常见语法错误
            if stripped.startswith('如果') and '那么' not in stripped:
                self.syntax_errors.append((line_num, "'如果' 语句缺少 '那么'"))

            if stripped.startswith('重复') and '次' not in stripped and '执行' not in stripped:
                self.syntax_errors.append((line_num, "'重复' 语句缺少 '次' 或 '执行'"))

            # 检查变量声明格式
            if stripped.startswith('变量:') or stripped.startswith('列表:'):
                if ':' in stripped:
                    value_part = stripped.split(':', 1)[1].strip()
                    if not value_part:
                        self.syntax_errors.append((line_num, "变量/列表声明缺少名称"))

        # 检查未闭合的括号
        for bracket, line_num in bracket_stack:
            self.syntax_errors.append((line_num, f"未闭合的括号 '{bracket}'"))

        # 检查未闭合的控制结构
        for keyword, line_num in control_stack:
            self.syntax_errors.append((line_num, f"控制结构 '{keyword}' 缺少 '结束'"))

        # 发送信号
        self.syntax_errors_changed.emit(self.syntax_errors)

        # 高亮错误行
        self.highlight_error_lines()

    def setup_completer(self) -> None:
        """设置自动补全"""
        self.completer = QCompleter(self.KEYWORDS, self)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.activated.connect(self.insert_completion)

    def insert_completion(self, completion: str) -> None:
        """插入补全文本"""
        tc = self.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        tc.movePosition(QTextCursor.Left)
        tc.movePosition(QTextCursor.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)

    def text_under_cursor(self) -> str:
        """获取光标下的文本"""
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def keyPressEvent(self, event) -> None:
        """键盘事件处理"""
        if self.completer.popup().isVisible():
            # 如果补全弹窗可见，处理特殊按键
            if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab):
                event.ignore()
                return

        super().keyPressEvent(event)

        # 获取当前输入的文本
        completion_prefix = self.text_under_cursor()

        if len(completion_prefix) < 1:
            self.completer.popup().hide()
            return

        if completion_prefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completion_prefix)
            self.completer.popup().setCurrentIndex(
                self.completer.completionModel().index(0, 0)
            )

        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0)
                    + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr)

    def highlight_error_lines(self) -> None:
        """高亮错误行"""
        # 清除之前的高亮
        extra_selections = []

        error_format = QTextCharFormat()
        error_format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
        error_format.setUnderlineColor(QColor("#FF0000"))

        error_lines = set(line_num for line_num, _ in self.syntax_errors)

        for line_num in error_lines:
            block = self.document().findBlockByLineNumber(line_num - 1)
            if block.isValid():
                selection = QPlainTextEdit.ExtraSelection()
                selection.format.setBackground(QColor("#FFEEEE"))
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor = QTextCursor(block)
                extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def lineNumberAreaWidth(self) -> int:
        """计算行号区域宽度"""
        digits = len(str(max(1, self.blockCount())))
        # 使用 horizontalAdvance 替代已弃用的 width()
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, newBlockCount: int) -> None:
        """更新行号区域宽度"""
        total_width = self.lineNumberAreaWidth() + self.foldingArea.width()
        self.setViewportMargins(total_width, 0, 0, 0)

    def updateLineNumberArea(self, rect: QRect, dy: int) -> None:
        """更新行号区域"""
        if dy:
            self.lineNumberArea.scroll(0, dy)
            self.foldingArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
            self.foldingArea.update(0, rect.y(), self.foldingArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """窗口大小改变事件"""
        super().resizeEvent(event)
        cr = self.contentsRect()
        line_num_width = self.lineNumberAreaWidth()
        fold_width = self.foldingArea.width()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), line_num_width, cr.height()))
        self.foldingArea.setGeometry(QRect(cr.left() + line_num_width, cr.top(), fold_width, cr.height()))

    def lineNumberAreaPaintEvent(self, event: QPaintEvent) -> None:
        """绘制行号区域"""
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor("#F0F0F0"))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QColor("#808080"))
                painter.drawText(0, top, self.lineNumberArea.width() - 3,
                               self.fontMetrics().height(), Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def update_fold_regions(self) -> None:
        """更新可折叠区域"""
        self.fold_regions.clear()
        text = self.toPlainText()
        lines = text.split('\n')

        stack = []  # 存储 (起始行号, 关键字)

        for line_num, line in enumerate(lines):
            stripped = line.strip()

            # 检查是否是折叠开始
            for keyword in self.FOLD_START_KEYWORDS:
                if keyword in stripped:
                    # 检查是否是有效的控制结构开始
                    if keyword == '如果' and '那么' in stripped:
                        stack.append(line_num)
                    elif keyword == '重复执行':
                        stack.append(line_num)
                    elif keyword == '重复' and '次' in stripped:
                        stack.append(line_num)
                    break

            # 检查是否是折叠结束
            if stripped == self.FOLD_END_KEYWORD:
                if stack:
                    start_line = stack.pop()
                    self.fold_regions[start_line] = line_num

        self.foldingArea.update()

    def foldingAreaPaintEvent(self, event: QPaintEvent) -> None:
        """绘制折叠区域"""
        painter = QPainter(self.foldingArea)
        painter.fillRect(event.rect(), QColor("#F0F0F0"))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                if blockNumber in self.fold_regions:
                    # 绘制折叠标记
                    is_folded = blockNumber in self.folded_blocks
                    self._draw_fold_marker(painter, top, is_folded)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def _draw_fold_marker(self, painter: QPainter, top: int, is_folded: bool) -> None:
        """绘制折叠标记（三角形）"""
        size = 8
        margin = 3
        center_y = top + self.fontMetrics().height() // 2

        painter.setPen(QColor("#606060"))
        painter.setBrush(QColor("#606060"))

        if is_folded:
            # 绘制向右的三角形（已折叠）
            points = [
                QPoint(margin, center_y - size // 2),
                QPoint(margin, center_y + size // 2),
                QPoint(margin + size, center_y)
            ]
        else:
            # 绘制向下的三角形（未折叠）
            points = [
                QPoint(margin, center_y - size // 3),
                QPoint(margin + size, center_y - size // 3),
                QPoint(margin + size // 2, center_y + size // 2)
            ]

        painter.drawPolygon(QPolygon(points))

    def foldingAreaMousePressEvent(self, event: QMouseEvent) -> None:
        """处理折叠区域的鼠标点击"""
        block = self.firstVisibleBlock()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid():
            if top <= event.y() < bottom:
                block_num = block.blockNumber()
                if block_num in self.fold_regions:
                    self.toggle_fold(block_num)
                break
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())

    def toggle_fold(self, start_line: int) -> None:
        """切换折叠状态"""
        if start_line not in self.fold_regions:
            return

        end_line = self.fold_regions[start_line]

        if start_line in self.folded_blocks:
            # 展开
            self.folded_blocks.remove(start_line)
            for line_num in range(start_line + 1, end_line + 1):
                block = self.document().findBlockByNumber(line_num)
                if block.isValid():
                    block.setVisible(True)
        else:
            # 折叠
            self.folded_blocks.add(start_line)
            for line_num in range(start_line + 1, end_line + 1):
                block = self.document().findBlockByNumber(line_num)
                if block.isValid():
                    block.setVisible(False)

        self.viewport().update()
        self.foldingArea.update()
        self.lineNumberArea.update()