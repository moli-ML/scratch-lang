#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Scratch 3.0 反编译器
将 .sb3 文件转换为 ScratchLang .sl 文件
"""
import json
import zipfile
import os
from typing import Dict, List, Any, Optional

class SB3Decompiler:
    """Scratch 3.0 项目反编译器"""

    def __init__(self):
        self.project = None
        self.sl_code = []

    def load_sb3(self, filepath: str) -> Dict[str, Any]:
        """加载 sb3 文件"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")

        with zipfile.ZipFile(filepath, 'r') as zf:
            project_json = zf.read('project.json').decode('utf-8')
            self.project = json.loads(project_json)

        return self.project

    def decompile(self, sb3_file: str, output_file: str = None):
        """反编译 sb3 文件为 sl 文件"""
        self.load_sb3(sb3_file)
        self.sl_code = []

        # 添加文件头
        self.sl_code.append(": 开始")
        self.sl_code.append("")

        # 处理所有 targets
        for target in self.project.get('targets', []):
            self._process_target(target)

        # 生成输出
        sl_content = '\n'.join(self.sl_code)

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(sl_content)

        return sl_content

    def _process_target(self, target: Dict[str, Any]):
        """处理一个 target（舞台或角色）"""
        is_stage = target.get('isStage', False)
        name = target.get('name', 'Sprite1')

        # 添加角色/舞台声明
        if is_stage:
            self.sl_code.append("@ 舞台")
        else:
            self.sl_code.append(f"# {name}")

        # 处理变量
        variables = target.get('variables', {})
        for var_id, var_data in variables.items():
            var_name = var_data[0]
            var_value = var_data[1]
            self.sl_code.append(f"变量: {var_name} = {var_value}")

        # 处理列表
        lists = target.get('lists', {})
        for list_id, list_data in lists.items():
            list_name = list_data[0]
            self.sl_code.append(f"列表: {list_name}")

        # 处理造型
        costumes = target.get('costumes', [])
        for costume in costumes:
            costume_name = costume.get('name', '')
            self.sl_code.append(f"// 造型: {costume_name}")

        # 处理音效
        sounds = target.get('sounds', [])
        for sound in sounds:
            sound_name = sound.get('name', '')
            self.sl_code.append(f"// 音效: {sound_name}")

        self.sl_code.append("")

        # 处理脚本
        blocks = target.get('blocks', {})
        self._process_scripts(blocks)

        self.sl_code.append("")

    def _process_scripts(self, blocks: Dict[str, Any]):
        """处理所有脚本"""
        # 找到所有顶层块（topLevel=True）
        top_blocks = [bid for bid, block in blocks.items()
                     if isinstance(block, dict) and block.get('topLevel', False)]

        for block_id in top_blocks:
            script = self._convert_block_chain(blocks, block_id)
            if script:
                self.sl_code.extend(script)
                self.sl_code.append("")

    def _convert_block_chain(self, blocks: Dict[str, Any], block_id: str, indent: int = 0) -> List[str]:
        """转换一个块链"""
        result = []
        current_id = block_id
        indent_str = "  " * indent

        while current_id:
            block = blocks.get(current_id)
            if not block or not isinstance(block, dict):
                break

            opcode = block.get('opcode', '')

            # 转换块
            line = self._convert_block(blocks, current_id, block, indent)
            if line:
                result.append(indent_str + line)

            # 处理子块（如重复、如果等）
            if opcode in ['control_repeat', 'control_forever', 'control_if', 'control_if_else']:
                substack = block.get('inputs', {}).get('SUBSTACK')
                if substack and substack[1]:
                    sub_lines = self._convert_block_chain(blocks, substack[1], indent + 1)
                    result.extend(sub_lines)

                if opcode == 'control_if_else':
                    result.append(indent_str + "  否则")
                    substack2 = block.get('inputs', {}).get('SUBSTACK2')
                    if substack2 and substack2[1]:
                        sub_lines = self._convert_block_chain(blocks, substack2[1], indent + 1)
                        result.extend(sub_lines)

                result.append(indent_str + "  结束")

            # 移动到下一个块
            current_id = block.get('next')

        return result

    def _convert_block(self, blocks: Dict[str, Any], block_id: str, block: Dict[str, Any], indent: int) -> Optional[str]:
        """转换单个块为 ScratchLang 语法"""
        opcode = block.get('opcode', '')

        # 事件块
        if opcode == 'event_whenflagclicked':
            return "当绿旗被点击"

        # 动作块
        elif opcode == 'motion_movesteps':
            steps = self._get_input_value(blocks, block, 'STEPS')
            return f"移动 {steps} 步"

        elif opcode == 'motion_turnright':
            degrees = self._get_input_value(blocks, block, 'DEGREES')
            return f"旋转右 {degrees} 度"

        elif opcode == 'motion_turnleft':
            degrees = self._get_input_value(blocks, block, 'DEGREES')
            return f"旋转左 {degrees} 度"

        # 外观块
        elif opcode == 'looks_say':
            message = self._get_input_value(blocks, block, 'MESSAGE')
            return f"说 {message}"

        elif opcode == 'looks_sayforsecs':
            message = self._get_input_value(blocks, block, 'MESSAGE')
            secs = self._get_input_value(blocks, block, 'SECS')
            return f"说 {message} 持续 {secs} 秒"

        # 控制块
        elif opcode == 'control_repeat':
            times = self._get_input_value(blocks, block, 'TIMES')
            return f"重复 {times} 次"

        elif opcode == 'control_forever':
            return "重复执行"

        elif opcode == 'control_if':
            condition = self._get_input_value(blocks, block, 'CONDITION')
            return f"如果 {condition} 那么"

        elif opcode == 'control_wait':
            duration = self._get_input_value(blocks, block, 'DURATION')
            return f"等待 {duration} 秒"

        # 变量块
        elif opcode == 'data_setvariableto':
            var_name = self._get_field_value(block, 'VARIABLE')
            value = self._get_input_value(blocks, block, 'VALUE')
            return f"设置 ~{var_name} 为 {value}"

        # 画笔块
        elif opcode == 'pen_penDown':
            return "落笔"

        elif opcode == 'pen_penUp':
            return "抬笔"

        # 默认：显示 opcode
        else:
            return f"// 未支持的块: {opcode}"

    def _get_input_value(self, blocks: Dict[str, Any], block: Dict[str, Any], input_name: str) -> str:
        """获取输入值"""
        inputs = block.get('inputs', {})
        input_data = inputs.get(input_name)

        if not input_data:
            return "?"

        # 处理不同类型的输入
        if isinstance(input_data, list) and len(input_data) >= 2:
            input_type = input_data[0]
            input_value = input_data[1]

            # 直接值
            if input_type == 1:
                if isinstance(input_value, list) and len(input_value) >= 2:
                    value_type = input_value[0]
                    value = input_value[1]
                    if value_type == 4:  # 数字
                        return str(value)
                    elif value_type == 10:  # 字符串
                        return f'"{value}"'

            # 块引用
            elif isinstance(input_value, str):
                ref_block = blocks.get(input_value)
                if ref_block:
                    return self._convert_reporter_block(blocks, ref_block)

        return "?"

    def _convert_reporter_block(self, blocks: Dict[str, Any], block: Dict[str, Any]) -> str:
        """转换报告块"""
        opcode = block.get('opcode', '')

        if opcode == 'data_variable':
            var_name = self._get_field_value(block, 'VARIABLE')
            return f"~{var_name}"

        elif opcode == 'operator_add':
            num1 = self._get_input_value(blocks, block, 'NUM1')
            num2 = self._get_input_value(blocks, block, 'NUM2')
            return f"({num1} + {num2})"

        return "?"

    def _get_field_value(self, block: Dict[str, Any], field_name: str) -> str:
        """获取字段值"""
        fields = block.get('fields', {})
        field_data = fields.get(field_name)

        if field_data and isinstance(field_data, list) and len(field_data) > 0:
            return str(field_data[0])

        return "?"

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python decompiler.py <输入文件.sb3> [-o 输出文件.sl]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[3] if len(sys.argv) > 3 else input_file.replace('.sb3', '.sl')

    decompiler = SB3Decompiler()
    decompiler.decompile(input_file, output_file)
    print(f"✅ 反编译成功: {output_file}")
