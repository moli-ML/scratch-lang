"""
exceptions.py 单元测试
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler.exceptions import (
    ScratchLangError,
    ParseError,
    CompileError,
    AssetError,
    SecurityError
)


class TestScratchLangError:
    """ScratchLangError 测试类"""

    def test_basic_error(self):
        """测试基本错误"""
        error = ScratchLangError("测试错误")
        assert str(error) == "测试错误"

    def test_error_with_line(self):
        """测试带行号的错误"""
        error = ScratchLangError("语法错误", line=10)
        assert "第 10 行" in str(error)
        assert "语法错误" in str(error)

    def test_error_with_line_and_column(self):
        """测试带行号和列号的错误"""
        error = ScratchLangError("未知符号", line=5, column=12)
        assert "第 5 行" in str(error)
        assert "第 12 列" in str(error)
        assert "未知符号" in str(error)


class TestParseError:
    """ParseError 测试类"""

    def test_is_subclass(self):
        """测试是 ScratchLangError 的子类"""
        assert issubclass(ParseError, ScratchLangError)

    def test_can_be_raised(self):
        """测试可以被抛出"""
        with pytest.raises(ParseError):
            raise ParseError("解析失败")


class TestCompileError:
    """CompileError 测试类"""

    def test_is_subclass(self):
        """测试是 ScratchLangError 的子类"""
        assert issubclass(CompileError, ScratchLangError)

    def test_can_be_raised(self):
        """测试可以被抛出"""
        with pytest.raises(CompileError):
            raise CompileError("编译失败")


class TestAssetError:
    """AssetError 测试类"""

    def test_is_subclass(self):
        """测试是 ScratchLangError 的子类"""
        assert issubclass(AssetError, ScratchLangError)

    def test_can_be_raised(self):
        """测试可以被抛出"""
        with pytest.raises(AssetError):
            raise AssetError("资源加载失败")


class TestSecurityError:
    """SecurityError 测试类"""

    def test_is_subclass(self):
        """测试是 ScratchLangError 的子类"""
        assert issubclass(SecurityError, ScratchLangError)

    def test_can_be_raised(self):
        """测试可以被抛出"""
        with pytest.raises(SecurityError):
            raise SecurityError("安全检查失败")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
