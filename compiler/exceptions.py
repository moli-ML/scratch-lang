"""
ScratchLang 自定义异常类
"""


class ScratchLangError(Exception):
    """ScratchLang 基础异常类"""

    def __init__(self, message: str, line: int = None, column: int = None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if self.line is not None:
            if self.column is not None:
                return f"第 {self.line} 行, 第 {self.column} 列: {self.message}"
            return f"第 {self.line} 行: {self.message}"
        return self.message


class ParseError(ScratchLangError):
    """语法解析错误"""
    pass


class CompileError(ScratchLangError):
    """编译错误"""
    pass


class AssetError(ScratchLangError):
    """资源文件错误"""
    pass


class SecurityError(ScratchLangError):
    """安全相关错误"""
    pass
