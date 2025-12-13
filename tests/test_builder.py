"""
builder.py 单元测试
"""
import pytest
import os
import sys
import tempfile
import zipfile
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler.builder import SB3Builder


class TestSB3Builder:
    """SB3Builder 测试类"""

    def setup_method(self):
        """每个测试方法前执行"""
        self.builder = SB3Builder()

    def test_initial_project_structure(self):
        """测试初始项目结构"""
        assert "targets" in self.builder.project
        assert "monitors" in self.builder.project
        assert "extensions" in self.builder.project
        assert "meta" in self.builder.project

    def test_add_sprite(self):
        """测试添加角色"""
        self.builder.add_sprite("小猫")
        assert self.builder.current_sprite is not None
        assert self.builder.current_sprite["name"] == "小猫"
        assert self.builder.current_sprite["isStage"] is False

    def test_add_stage(self):
        """测试添加舞台"""
        self.builder.add_sprite("Stage", is_stage=True)
        assert self.builder.stage is not None
        assert self.builder.stage["isStage"] is True

    def test_switch_to_stage(self):
        """测试切换到舞台"""
        self.builder.add_sprite("Stage", is_stage=True)
        self.builder.add_sprite("小猫")
        self.builder.switch_to_stage()
        assert self.builder.current_sprite["isStage"] is True

    def test_add_variable(self):
        """测试添加变量"""
        self.builder.add_sprite("小猫")
        self.builder.add_variable("分数", 0)
        variables = self.builder.current_sprite.get("variables", {})
        var_names = [v[0] for v in variables.values()]
        assert "分数" in var_names

    def test_add_variable_with_value(self):
        """测试添加带初始值的变量"""
        self.builder.add_sprite("小猫")
        self.builder.add_variable("速度", 10)
        variables = self.builder.current_sprite.get("variables", {})
        for var_data in variables.values():
            if var_data[0] == "速度":
                assert var_data[1] == 10

    def test_add_list(self):
        """测试添加列表"""
        self.builder.add_sprite("小猫")
        self.builder.add_list("数据", [])
        lists = self.builder.current_sprite.get("lists", {})
        list_names = [l[0] for l in lists.values()]
        assert "数据" in list_names

    def test_add_block(self):
        """测试添加积木"""
        self.builder.add_sprite("小猫")
        block_id = self.builder.add_block(
            "motion_movesteps",
            {"STEPS": [1, [4, "10"]]},
            {},
            None,
            True
        )
        assert block_id is not None
        assert block_id in self.builder.current_sprite["blocks"]

    def test_add_shadow_block(self):
        """测试添加阴影积木"""
        self.builder.add_sprite("小猫")
        shadow_id = self.builder.add_shadow_block(
            "sensing_keyoptions",
            {"KEY_OPTION": ["space", None]}
        )
        assert shadow_id is not None
        block = self.builder.current_sprite["blocks"][shadow_id]
        assert block["shadow"] is True

    def test_finalize_sprite(self):
        """测试完成角色"""
        self.builder.add_sprite("小猫")
        self.builder.finalize_sprite()
        targets = self.builder.project["targets"]
        sprite_names = [t["name"] for t in targets]
        assert "小猫" in sprite_names

    def test_save_creates_valid_sb3(self):
        """测试保存创建有效的 sb3 文件"""
        self.builder.add_sprite("Stage", is_stage=True)
        self.builder.finalize_sprite()
        self.builder.add_sprite("小猫")
        self.builder.add_block("event_whenflagclicked", {}, {}, None, True)
        self.builder.finalize_sprite()

        with tempfile.NamedTemporaryFile(suffix='.sb3', delete=False) as f:
            temp_path = f.name

        try:
            self.builder.save(temp_path)
            assert os.path.exists(temp_path)

            # 验证是有效的 zip 文件
            assert zipfile.is_zipfile(temp_path)

            # 验证包含 project.json
            with zipfile.ZipFile(temp_path, 'r') as zf:
                assert "project.json" in zf.namelist()

                # 验证 project.json 是有效的 JSON
                with zf.open("project.json") as pf:
                    project = json.load(pf)
                    assert "targets" in project
                    assert len(project["targets"]) >= 2  # 舞台 + 角色
        finally:
            os.unlink(temp_path)


class TestSB3BuilderBlocks:
    """SB3Builder 积木相关测试"""

    def setup_method(self):
        self.builder = SB3Builder()
        self.builder.add_sprite("小猫")

    def test_block_has_correct_structure(self):
        """测试积木有正确的结构"""
        block_id = self.builder.add_block(
            "motion_movesteps",
            {"STEPS": [1, [4, "10"]]},
            {},
            None,
            True
        )
        block = self.builder.current_sprite["blocks"][block_id]
        assert "opcode" in block
        assert "inputs" in block
        assert "fields" in block
        assert "topLevel" in block

    def test_top_level_block_has_position(self):
        """测试顶层积木有位置信息"""
        block_id = self.builder.add_block(
            "event_whenflagclicked",
            {},
            {},
            None,
            True
        )
        block = self.builder.current_sprite["blocks"][block_id]
        assert block["topLevel"] is True
        assert "x" in block
        assert "y" in block

    def test_non_top_level_block_no_position(self):
        """测试非顶层积木没有位置信息"""
        parent_id = self.builder.add_block(
            "event_whenflagclicked",
            {},
            {},
            None,
            True
        )
        block_id = self.builder.add_block(
            "motion_movesteps",
            {"STEPS": [1, [4, "10"]]},
            {},
            parent_id,
            False
        )
        block = self.builder.current_sprite["blocks"][block_id]
        assert block["topLevel"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
