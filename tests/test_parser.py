"""
parser.py 单元测试
"""
import pytest
import os
import sys
import tempfile

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler.parser import ScratchLangParser
from compiler.exceptions import SecurityError


class TestScratchLangParser:
    """ScratchLangParser 测试类"""

    def setup_method(self):
        """每个测试方法前执行"""
        self.parser = ScratchLangParser()

    # ==================== 基础解析测试 ====================

    def test_parse_empty_code(self):
        """测试解析空代码"""
        result = self.parser.parse("")
        assert result is not None
        assert result.project is not None

    def test_parse_comment_only(self):
        """测试只有注释的代码"""
        code = "// 这是注释\n// 另一行注释"
        result = self.parser.parse(code)
        assert result is not None

    def test_parse_start_marker(self):
        """测试开始标记"""
        code = ": 开始"
        result = self.parser.parse(code)
        assert result is not None
        # 应该自动创建舞台
        assert any(t["isStage"] for t in result.project["targets"])

    # ==================== 角色和舞台测试 ====================

    def test_parse_sprite(self):
        """测试角色声明"""
        code = "# 小猫"
        result = self.parser.parse(code)
        targets = result.project["targets"]
        sprite_names = [t["name"] for t in targets if not t["isStage"]]
        assert "小猫" in sprite_names

    def test_parse_stage(self):
        """测试舞台声明"""
        code = "@ 舞台"
        result = self.parser.parse(code)
        targets = result.project["targets"]
        assert any(t["isStage"] for t in targets)

    def test_parse_multiple_sprites(self):
        """测试多个角色"""
        code = """
# 小猫
# 小狗
# 小鸟
"""
        result = self.parser.parse(code)
        targets = result.project["targets"]
        sprite_names = [t["name"] for t in targets if not t["isStage"]]
        assert "小猫" in sprite_names
        assert "小狗" in sprite_names
        assert "小鸟" in sprite_names

    # ==================== 事件积木测试 ====================

    def test_parse_green_flag_event(self):
        """测试绿旗事件"""
        code = """
# 小猫
当绿旗被点击
  移动 10 步
"""
        result = self.parser.parse(code)
        sprite = next(t for t in result.project["targets"] if t["name"] == "小猫")
        blocks = sprite["blocks"]
        opcodes = [b["opcode"] for b in blocks.values() if isinstance(b, dict)]
        assert "event_whenflagclicked" in opcodes

    def test_parse_key_press_event(self):
        """测试按键事件"""
        code = """
# 小猫
当按下 空格 键
  移动 10 步
"""
        result = self.parser.parse(code)
        sprite = next(t for t in result.project["targets"] if t["name"] == "小猫")
        blocks = sprite["blocks"]
        opcodes = [b["opcode"] for b in blocks.values() if isinstance(b, dict)]
        assert "event_whenkeypressed" in opcodes

    # ==================== 动作积木测试 ====================

    def test_parse_move_block(self):
        """测试移动积木"""
        code = """
# 小猫
当绿旗被点击
  移动 10 步
"""
        result = self.parser.parse(code)
        sprite = next(t for t in result.project["targets"] if t["name"] == "小猫")
        blocks = sprite["blocks"]
        opcodes = [b["opcode"] for b in blocks.values() if isinstance(b, dict)]
        assert "motion_movesteps" in opcodes

    def test_parse_goto_xy(self):
        """测试移到坐标"""
        code = """
# 小猫
当绿旗被点击
  移到 100 200
"""
        result = self.parser.parse(code)
        sprite = next(t for t in result.project["targets"] if t["name"] == "小猫")
        blocks = sprite["blocks"]
        opcodes = [b["opcode"] for b in blocks.values() if isinstance(b, dict)]
        assert "motion_gotoxy" in opcodes

    def test_parse_turn_right(self):
        """测试右转"""
        code = """
# 小猫
当绿旗被点击
  旋转右 90 度
"""
        result = self.parser.parse(code)
        sprite = next(t for t in result.project["targets"] if t["name"] == "小猫")
        blocks = sprite["blocks"]
        opcodes = [b["opcode"] for b in blocks.values() if isinstance(b, dict)]
        assert "motion_turnright" in opcodes

    # ==================== 控制积木测试 ====================

    def test_parse_repeat_block(self):
        """测试重复积木"""
        code = """
# 小猫
当绿旗被点击
  重复 10 次
    移动 10 步
  结束
"""
        result = self.parser.parse(code)
        sprite = next(t for t in result.project["targets"] if t["name"] == "小猫")
        blocks = sprite["blocks"]
        opcodes = [b["opcode"] for b in blocks.values() if isinstance(b, dict)]
        assert "control_repeat" in opcodes

    def test_parse_forever_block(self):
        """测试重复执行积木"""
        code = """
# 小猫
当绿旗被点击
  重复执行
    移动 10 步
  结束
"""
        result = self.parser.parse(code)
        sprite = next(t for t in result.project["targets"] if t["name"] == "小猫")
        blocks = sprite["blocks"]
        opcodes = [b["opcode"] for b in blocks.values() if isinstance(b, dict)]
        assert "control_forever" in opcodes

    def test_parse_if_block(self):
        """测试如果积木"""
        code = """
# 小猫
当绿旗被点击
  如果 1 > 0 那么
    移动 10 步
  结束
"""
        result = self.parser.parse(code)
        sprite = next(t for t in result.project["targets"] if t["name"] == "小猫")
        blocks = sprite["blocks"]
        opcodes = [b["opcode"] for b in blocks.values() if isinstance(b, dict)]
        assert "control_if" in opcodes

    def test_parse_if_else_block(self):
        """测试如果否则积木"""
        code = """
# 小猫
当绿旗被点击
  如果 1 > 0 那么
    移动 10 步
  否则
    移动 -10 步
  结束
"""
        result = self.parser.parse(code)
        sprite = next(t for t in result.project["targets"] if t["name"] == "小猫")
        blocks = sprite["blocks"]
        opcodes = [b["opcode"] for b in blocks.values() if isinstance(b, dict)]
        assert "control_if_else" in opcodes

    # ==================== 变量测试 ====================

    def test_parse_variable_declaration(self):
        """测试变量声明"""
        code = """
# 小猫
变量: 分数 = 0
"""
        result = self.parser.parse(code)
        sprite = next(t for t in result.project["targets"] if t["name"] == "小猫")
        variables = sprite.get("variables", {})
        var_names = [v[0] for v in variables.values()]
        assert "分数" in var_names

    def test_parse_variable_with_initial_value(self):
        """测试带初始值的变量"""
        code = """
# 小猫
变量: 速度 = 10
"""
        result = self.parser.parse(code)
        sprite = next(t for t in result.project["targets"] if t["name"] == "小猫")
        variables = sprite.get("variables", {})
        for var_id, var_data in variables.items():
            if var_data[0] == "速度":
                assert var_data[1] == 10

    # ==================== 比较运算符测试 ====================

    def test_parse_greater_than(self):
        """测试大于运算符"""
        code = """
# 小猫
当绿旗被点击
  如果 10 > 5 那么
    移动 10 步
  结束
"""
        result = self.parser.parse(code)
        sprite = next(t for t in result.project["targets"] if t["name"] == "小猫")
        blocks = sprite["blocks"]
        opcodes = [b["opcode"] for b in blocks.values() if isinstance(b, dict)]
        assert "operator_gt" in opcodes

    def test_parse_less_than(self):
        """测试小于运算符"""
        code = """
# 小猫
当绿旗被点击
  如果 5 < 10 那么
    移动 10 步
  结束
"""
        result = self.parser.parse(code)
        sprite = next(t for t in result.project["targets"] if t["name"] == "小猫")
        blocks = sprite["blocks"]
        opcodes = [b["opcode"] for b in blocks.values() if isinstance(b, dict)]
        assert "operator_lt" in opcodes

    def test_parse_greater_equal(self):
        """测试大于等于运算符 (应该生成 not + lt)"""
        code = """
# 小猫
当绿旗被点击
  如果 10 >= 5 那么
    移动 10 步
  结束
"""
        result = self.parser.parse(code)
        sprite = next(t for t in result.project["targets"] if t["name"] == "小猫")
        blocks = sprite["blocks"]
        opcodes = [b["opcode"] for b in blocks.values() if isinstance(b, dict)]
        # >= 实现为 not (a < b)
        assert "operator_not" in opcodes
        assert "operator_lt" in opcodes

    def test_parse_less_equal(self):
        """测试小于等于运算符 (应该生成 not + gt)"""
        code = """
# 小猫
当绿旗被点击
  如果 5 <= 10 那么
    移动 10 步
  结束
"""
        result = self.parser.parse(code)
        sprite = next(t for t in result.project["targets"] if t["name"] == "小猫")
        blocks = sprite["blocks"]
        opcodes = [b["opcode"] for b in blocks.values() if isinstance(b, dict)]
        # <= 实现为 not (a > b)
        assert "operator_not" in opcodes
        assert "operator_gt" in opcodes

    # ==================== 安全测试 ====================

    def test_path_traversal_attack_blocked(self):
        """测试路径遍历攻击被阻止"""
        self.parser.current_dir = tempfile.gettempdir()
        with pytest.raises(SecurityError):
            self.parser.resolve_path("../../../etc/passwd")

    def test_safe_path_allowed(self):
        """测试安全路径被允许"""
        with tempfile.TemporaryDirectory() as tmpdir:
            self.parser.current_dir = tmpdir
            # 创建子目录
            subdir = os.path.join(tmpdir, "images")
            os.makedirs(subdir)
            # 安全路径应该被允许
            result = self.parser.resolve_path("images")
            assert result == os.path.normpath(os.path.join(tmpdir, "images"))

    # ==================== 文件解析测试 ====================

    def test_parse_file(self):
        """测试从文件解析"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sl', delete=False, encoding='utf-8') as f:
            f.write("""
: 开始
# 小猫
当绿旗被点击
  移动 10 步
""")
            f.flush()
            temp_path = f.name

        try:
            result = self.parser.parse_file(temp_path)
            assert result is not None
            targets = result.project["targets"]
            sprite_names = [t["name"] for t in targets if not t["isStage"]]
            assert "小猫" in sprite_names
        finally:
            os.unlink(temp_path)


class TestParserHelpers:
    """解析器辅助方法测试"""

    def setup_method(self):
        self.parser = ScratchLangParser()

    def test_split_by_delimiter_plus(self):
        """测试按加号分割"""
        result = self.parser._split_by_delimiter("a + b + c", '+')
        assert result == ["a", "b", "c"]

    def test_split_by_delimiter_comma(self):
        """测试按逗号分割"""
        result = self.parser._split_by_delimiter("a, b, c", ',')
        assert result == ["a", "b", "c"]

    def test_split_preserves_quotes(self):
        """测试分割时保留引号内容"""
        result = self.parser._split_by_delimiter('"a+b" + c', '+')
        assert result == ['"a+b"', "c"]

    def test_split_preserves_parentheses(self):
        """测试分割时保留括号内容"""
        result = self.parser._split_by_delimiter("func(a, b) + c", '+')
        assert result == ["func(a, b)", "c"]

    def test_clean_path(self):
        """测试路径清理"""
        result = self.parser.clean_path('  "path/to/file.png"  ')
        assert result == "path/to/file.png"

    def test_get_key_name_space(self):
        """测试按键名称转换 - 空格"""
        result = self.parser._get_key_name("空格")
        assert result == "space"

    def test_get_key_name_arrow(self):
        """测试按键名称转换 - 方向键"""
        assert self.parser._get_key_name("上") == "up arrow"
        assert self.parser._get_key_name("下") == "down arrow"
        assert self.parser._get_key_name("左") == "left arrow"
        assert self.parser._get_key_name("右") == "right arrow"

    def test_get_key_name_letter(self):
        """测试按键名称转换 - 字母"""
        assert self.parser._get_key_name("a") == "a"
        assert self.parser._get_key_name("A") == "a"


class TestNewFeatures:
    """新功能测试"""

    def setup_method(self):
        self.parser = ScratchLangParser()

    def test_block_comments(self):
        """测试块注释"""
        code = """
/* 这是块注释
   可以跨多行 */
# 小猫
当绿旗被点击
  移动 10 步
"""
        result = self.parser.parse(code)
        assert result is not None

    def test_multiline_strings(self):
        """测试多行字符串"""
        code = '''
# 小猫
当绿旗被点击
  说 """这是
多行
字符串""" 2 秒
'''
        cleaned = self.parser._process_multiline_strings(code)
        assert '"""' not in cleaned
        assert '\\n' in cleaned

    def test_escape_characters(self):
        """测试转义字符"""
        text = "Hello\\nWorld\\tTab"
        result = self.parser._process_escape_chars(text)
        assert '\n' in result
        assert '\t' in result

    def test_extract_js_blocks(self):
        """测试提取 JS 代码块"""
        code = """
#code#
console.log('test');
#end#

# 小猫
"""
        cleaned, js_blocks = self.parser._extract_js_blocks(code)
        assert len(js_blocks) == 1
        assert 'console.log' in js_blocks[0]
        assert '#code#' not in cleaned

    def test_js_blocks_as_extensions(self):
        """测试 JS 代码块转换为扩展"""
        code = """
# 小猫
当绿旗被点击
#code#
console.log('block1');
#end#
    说 "test" 2 秒
#code#
console.log('block2');
#end#
结束
"""
        result = self.parser.parse(code)
        extensions = result.project['extensions']
        assert 'inlinecode1' in extensions
        assert 'inlinecode2' in extensions

        # 验证 JS 代码保存在 extensionURLs 中（TurboWarp 格式）
        extension_urls = result.project.get('extensionURLs', {})
        assert 'inlinecode1' in extension_urls
        assert 'inlinecode2' in extension_urls
        assert extension_urls['inlinecode1'].startswith('data:application/javascript,')
        assert 'console.log' in extension_urls['inlinecode1']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
