"""
blocks.py 单元测试
"""
import pytest
import re
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler.blocks import BlockDefinitions


class TestBlockDefinitions:
    """BlockDefinitions 测试类"""

    def test_get_all_blocks_not_empty(self):
        """测试获取所有积木不为空"""
        blocks = BlockDefinitions.get_all_blocks()
        assert len(blocks) > 0

    def test_all_blocks_have_opcode(self):
        """测试所有积木都有 opcode"""
        blocks = BlockDefinitions.get_all_blocks()
        for name, block in blocks.items():
            assert "opcode" in block, f"积木 '{name}' 缺少 opcode"

    def test_all_patterns_are_valid_regex(self):
        """测试所有 pattern 都是有效的正则表达式"""
        blocks = BlockDefinitions.get_all_blocks()
        for name, block in blocks.items():
            if "pattern" in block:
                try:
                    re.compile(block["pattern"])
                except re.error as e:
                    pytest.fail(f"积木 '{name}' 的 pattern 无效: {e}")


class TestEventBlocks:
    """事件积木测试"""

    def test_green_flag_pattern(self):
        """测试绿旗点击模式"""
        pattern = BlockDefinitions.EVENTS["当绿旗被点击"]["pattern"]
        assert re.search(pattern, "当绿旗被点击")
        assert re.search(pattern, "when flag clicked")

    def test_key_press_pattern(self):
        """测试按键模式"""
        pattern = BlockDefinitions.EVENTS["当按下键"]["pattern"]
        match = re.search(pattern, "当按下 空格 键")
        assert match
        assert match.group(1).strip() == "空格"

    def test_broadcast_received_pattern(self):
        """测试收到广播模式"""
        pattern = BlockDefinitions.EVENTS["当收到"]["pattern"]
        match = re.search(pattern, "当收到 消息1")
        assert match
        assert match.group(1).strip() == "消息1"


class TestMotionBlocks:
    """动作积木测试"""

    def test_move_steps_pattern(self):
        """测试移动步数模式"""
        pattern = BlockDefinitions.MOTION["移动步"]["pattern"]
        match = re.search(pattern, "移动 10 步")
        assert match
        assert match.group(1).strip() == "10"

    def test_move_steps_with_variable(self):
        """测试移动步数带变量"""
        pattern = BlockDefinitions.MOTION["移动步"]["pattern"]
        match = re.search(pattern, "移动 ~速度 步")
        assert match
        assert match.group(1).strip() == "~速度"

    def test_turn_right_pattern(self):
        """测试右转模式"""
        pattern = BlockDefinitions.MOTION["旋转右"]["pattern"]
        match = re.search(pattern, "旋转右 90 度")
        assert match
        assert match.group(1).strip() == "90"

    def test_goto_xy_pattern(self):
        """测试移到坐标模式"""
        pattern = BlockDefinitions.MOTION["移到xy"]["pattern"]
        match = re.search(pattern, "移到 100 200")
        assert match
        assert match.group(1).strip() == "100"
        assert match.group(2).strip() == "200"

    def test_glide_pattern(self):
        """测试滑行模式"""
        pattern = BlockDefinitions.MOTION["滑行xy"]["pattern"]
        match = re.search(pattern, "在 1 秒内滑行到 100 200")
        assert match
        assert match.group(1).strip() == "1"
        assert match.group(2).strip() == "100"
        assert match.group(3).strip() == "200"


class TestControlBlocks:
    """控制积木测试"""

    def test_wait_pattern(self):
        """测试等待模式"""
        pattern = BlockDefinitions.CONTROL["等待"]["pattern"]
        match = re.search(pattern, "等待 1 秒")
        assert match
        assert match.group(1).strip() == "1"

    def test_repeat_pattern(self):
        """测试重复模式"""
        pattern = BlockDefinitions.CONTROL["重复"]["pattern"]
        match = re.search(pattern, "重复 10 次")
        assert match
        assert match.group(1).strip() == "10"

    def test_forever_pattern(self):
        """测试重复执行模式"""
        pattern = BlockDefinitions.CONTROL["重复执行"]["pattern"]
        assert re.search(pattern, "重复执行")
        assert re.search(pattern, "forever")

    def test_if_pattern(self):
        """测试如果模式"""
        pattern = BlockDefinitions.CONTROL["如果"]["pattern"]
        match = re.search(pattern, "如果 x > 0 那么")
        assert match
        assert match.group(1).strip() == "x > 0"

    def test_broadcast_pattern(self):
        """测试广播模式"""
        pattern = BlockDefinitions.CONTROL["广播"]["pattern"]
        match = re.search(pattern, "广播 消息1")
        assert match
        assert match.group(1).strip() == "消息1"


class TestVariableBlocks:
    """变量积木测试"""

    def test_set_variable_pattern(self):
        """测试设置变量模式"""
        pattern = BlockDefinitions.VARIABLES["设置变量"]["pattern"]
        match = re.search(pattern, "设置 分数 为 100")
        assert match
        assert match.group(1).strip() == "分数"
        assert match.group(2).strip() == "100"

    def test_change_variable_pattern(self):
        """测试变量增加模式"""
        pattern = BlockDefinitions.VARIABLES["变量增加"]["pattern"]
        match = re.search(pattern, "将 分数 增加 10")
        assert match
        assert match.group(1).strip() == "分数"
        assert match.group(2).strip() == "10"


class TestPenBlocks:
    """画笔积木测试"""

    def test_pen_down_pattern(self):
        """测试落笔模式"""
        pattern = BlockDefinitions.PEN["落笔"]["pattern"]
        assert re.search(pattern, "落笔")

    def test_pen_up_pattern(self):
        """测试抬笔模式"""
        pattern = BlockDefinitions.PEN["抬笔"]["pattern"]
        assert re.search(pattern, "抬笔")

    def test_pen_color_pattern(self):
        """测试笔迹颜色模式"""
        pattern = BlockDefinitions.PEN["笔迹颜色"]["pattern"]
        match = re.search(pattern, "将笔的颜色设为 #FF0000")
        assert match
        assert match.group(1) == "#FF0000"

    def test_pen_size_pattern(self):
        """测试笔迹粗细模式"""
        pattern = BlockDefinitions.PEN["笔迹粗细"]["pattern"]
        match = re.search(pattern, "将笔的粗细设为 5")
        assert match
        assert match.group(1) == "5"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
