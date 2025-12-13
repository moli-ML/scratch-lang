"""
语法解析器 - ScratchLang Compiler (v2.5 最终修复版)
修复了所有 shadow block 的 parent 链接问题
"""
import re
import os
from .builder import SB3Builder
from .blocks import BlockDefinitions
from .exceptions import ParseError, SecurityError, AssetError
from .constants import (
    SPECIAL_TARGETS, KEY_MAP, TARGET_STAGE,
    ROTATION_STYLES, STOP_OPTIONS, DRAG_MODES
)

class ScratchLangParser:
    def __init__(self):
        self.builder = SB3Builder()
        self.blocks_def = BlockDefinitions.get_all_blocks()
        self.has_stage = False
        self.current_dir = os.getcwd()

        # 使用常量模块中的映射
        self.SPECIAL_TARGETS = SPECIAL_TARGETS
        self.KEY_MAP = KEY_MAP
        
    def clean_path(self, path):
        """清理文件路径，去除不可见字符"""
        path = path.strip()
        path = ''.join(char for char in path if ord(char) >= 32 or char in '\t\n\r')
        path = path.strip('"\'""''')
        return path
    
    def resolve_path(self, path):
        """解析文件路径，防止路径遍历攻击"""
        path = self.clean_path(path)
        if os.path.isabs(path):
            resolved = os.path.normpath(path)
        else:
            resolved = os.path.normpath(os.path.join(self.current_dir, path))

        # 安全检查：确保解析后的路径在允许的目录内
        resolved_real = os.path.realpath(resolved)
        base_real = os.path.realpath(self.current_dir)

        # 检查路径是否在项目目录或其子目录内
        if not resolved_real.startswith(base_real + os.sep) and resolved_real != base_real:
            raise SecurityError(f"路径 '{path}' 超出项目目录范围，已拒绝访问")

        return resolved
    
    def parse_file(self, filepath):
        """解析文件"""
        self.current_dir = os.path.dirname(os.path.abspath(filepath))
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        return self.parse(code)
    
    def parse(self, code):
        """解析代码"""
        lines = code.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # 跳过空行和注释
            if not stripped or stripped.startswith('//'):
                i += 1
                continue
            
            # 开始标记
            if stripped.startswith(':'):
                if not self.has_stage:
                    self.builder.add_sprite("Stage", is_stage=True)
                    self.has_stage = True
                i += 1
                continue
            
            # 舞台声明
            if stripped.startswith('@'):
                if not self.has_stage:
                    self.builder.add_sprite("Stage", is_stage=True)
                    self.has_stage = True
                if self.builder.current_sprite is not None:
                    self.builder.finalize_sprite()
                self.builder.switch_to_stage()
                i += 1
                continue
            
            # 角色声明
            if stripped.startswith('#'):
                sprite_name = stripped[1:].strip()
                if not self.has_stage:
                    self.builder.add_sprite("Stage", is_stage=True)
                    self.has_stage = True
                if self.builder.current_sprite is not None:
                    self.builder.finalize_sprite()
                self.builder.add_sprite(sprite_name)
                i += 1
                continue
            
            # 关键字定义
            if ':' in stripped:
                parts = stripped.split(':', 1)
                if len(parts) == 2:
                    keyword, value = parts[0].strip(), parts[1].strip()
                    if self.handle_keyword(keyword, value):
                        i += 1
                        continue
            
            # 事件积木
            if self.is_event_block(stripped):
                i = self.parse_script(lines, i)
                continue
            
            i += 1
        
        if self.builder.current_sprite is not None:
            self.builder.finalize_sprite()
        
        return self.builder
    
    def handle_keyword(self, keyword, value):
        """处理关键字定义"""
        if keyword in ['背景', 'backdrop']:
            filepath = self.resolve_path(value)
            if not self.builder.current_sprite or not self.builder.current_sprite["isStage"]:
                self.builder.switch_to_stage()
            try:
                self.builder.add_backdrop(filepath)
                print(f"✅ 成功加载背景: {os.path.basename(filepath)}")
            except FileNotFoundError:
                print(f"⚠️ 警告: 背景文件不存在: {filepath}")
            except Exception as e:
                print(f"⚠️ 警告: 加载背景失败: {e}")
            return True
        
        if keyword in ['造型', 'costume']:
            filepath = self.resolve_path(value)
            if self.builder.current_sprite and self.builder.current_sprite["isStage"]:
                try:
                    self.builder.add_backdrop(filepath)
                    print(f"✅ 成功加载背景: {os.path.basename(filepath)}")
                except Exception as e:
                    print(f"⚠️ 警告: {e}")
            else:
                try:
                    self.builder.add_costume(filepath)
                    print(f"✅ 成功加载造型: {os.path.basename(filepath)}")
                except Exception as e:
                    print(f"⚠️ 警告: {e}")
            return True
        
        if keyword in ['音效', 'sound']:
            filepath = self.resolve_path(value)
            try:
                self.builder.add_sound(filepath)
                print(f"✅ 成功加载音效: {os.path.basename(filepath)}")
            except Exception as e:
                print(f"⚠️ 警告: {e}")
            return True
        
        if keyword in ['变量', 'var']:
            if '=' in value:
                var_name, var_value = value.split('=', 1)
                var_name = var_name.strip()
                var_value = var_value.strip()
                try:
                    var_value = float(var_value) if '.' in var_value else int(var_value)
                except ValueError:
                    var_value = var_value.strip('"\'')
                self.builder.add_variable(var_name, var_value)
            else:
                self.builder.add_variable(value.strip(), 0)
            return True
        
        if keyword in ['列表', 'list']:
            self.builder.add_list(value.strip(), [])
            return True
        
        return False

    def is_event_block(self, cmd):
        """判断是否是事件积木"""
        event_patterns = [v.get("pattern", "") for v in BlockDefinitions.EVENTS.values()]
        return any(re.search(pattern, cmd) for pattern in event_patterns if pattern)
    
    def parse_script(self, lines, start_idx):
        """解析一个脚本"""
        event_line = lines[start_idx].strip()
        event_id = self.create_block(event_line, top_level=True)
        idx, _ = self._parse_block_sequence(lines, start_idx + 1, event_id)
        
        # 🔥 事件块级别不需要"结束"，但如果有就跳过
        if idx < len(lines) and lines[idx].strip() in ['结束', 'end', '}']:
            idx += 1
        
        return idx
        
    def _parse_block_sequence(self, lines, start_idx, parent_id, base_indent=-1):
        """递归解析积木序列"""
        idx = start_idx
        first_id = None
        last_id = parent_id
        
        while idx < len(lines):
            line = lines[idx]
            stripped = line.strip()
            
            if not stripped or stripped.startswith('//'):
                idx += 1
                continue
            
            current_indent = len(line) - len(line.lstrip())
            
            # 🔥 修复1：只有在控制结构内才检查缩进
            if base_indent != -1 and current_indent <= base_indent:
                break
            
            # 🔥 修复2：只有在控制结构内才处理"结束"/"否则"
            if base_indent != -1:  # 在控制结构内
                if stripped in ['结束', 'end', '}', '否则', 'else']:
                    break
            
            # 🔥 修复3：在事件块级别，遇到新的事件块或角色定义才停止
            if self.is_event_block(stripped) or stripped.startswith(('#', '@', ':')):
                break
            
            if self.is_control_structure(stripped):
                idx, new_id = self.parse_control_block(lines, idx, last_id)
            else:
                new_id = self.create_block(stripped, parent=last_id)
                idx += 1
            
            if new_id:
                if not first_id:
                    first_id = new_id
                last_id = new_id
        
        return idx, first_id
        
    def is_control_structure(self, cmd):
        """判断是否是控制结构"""
        return any(keyword in cmd for keyword in ['重复', '如果', 'forever', 'if', 'repeat'])
    
    def parse_control_block(self, lines, start_idx, parent):
        """解析控制结构"""
        cmd = lines[start_idx].strip()
        block_id = self.create_block(cmd, parent=parent)
        
        if not block_id:
            return start_idx + 1, parent
        
        base_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())
        idx, first_child_id = self._parse_block_sequence(lines, start_idx + 1, None, base_indent=base_indent)
        
        if first_child_id:
            self.builder.current_sprite["blocks"][block_id]["inputs"]["SUBSTACK"] = [2, first_child_id]
            self.update_parent_chain(first_child_id, block_id)
        
        if idx < len(lines) and lines[idx].strip() in ['否则', 'else']:
            # 将 control_if 转换为 control_if_else
            if self.builder.current_sprite["blocks"][block_id]["opcode"] == "control_if":
                self.builder.current_sprite["blocks"][block_id]["opcode"] = "control_if_else"
            idx, first_else_child_id = self._parse_block_sequence(lines, idx + 1, None, base_indent=base_indent)
            if first_else_child_id:
                self.builder.current_sprite["blocks"][block_id]["inputs"]["SUBSTACK2"] = [2, first_else_child_id]
                self.update_parent_chain(first_else_child_id, block_id)
        
        # 🔥 跳过"结束"标记
        if idx < len(lines) and lines[idx].strip() in ['结束', 'end', '}']:
            idx += 1
        
        return idx, block_id

    def update_parent_chain(self, start_id, parent_id):
        """更新积木链的parent"""
        current_id = start_id
        while current_id:
            self.builder.current_sprite["blocks"][current_id]["parent"] = parent_id
            current_id = self.builder.current_sprite["blocks"][current_id].get("next")
    
    # ==================== 核心解析逻辑 ====================
    
    def create_block(self, cmd, parent=None, top_level=False):
        """根据命令创建积木"""
        if cmd.strip().startswith(('说 ', '想 ')):
            return self._create_say_think_block(cmd, parent, top_level)
        
        for block_def in self.blocks_def.values():
            if "pattern" not in block_def:
                continue
                
            pattern = block_def["pattern"]
            match = re.search(pattern, cmd)
            
            if match:
                opcode = block_def["opcode"]
                inputs = {}
                fields = {}
                shadow_blocks = {}  # 🔥 收集需要设置 parent 的 shadow blocks
                
                if "inputs" in block_def:
                    for input_name, group_idx in block_def["inputs"].items():
                        if isinstance(group_idx, int):
                            value = match.group(group_idx)
                            
                            if input_name == "CONDITION":
                                inputs[input_name] = self._parse_condition(value)
                            elif input_name == "KEY_OPTION" and opcode == "sensing_keypressed":
                                shadow_id = self._create_key_shadow(value)
                                inputs[input_name] = [1, shadow_id]
                                shadow_blocks[input_name] = shadow_id
                            elif input_name == "TOUCHINGOBJECTMENU":
                                shadow_id = self._create_touching_shadow(value)
                                inputs[input_name] = [1, shadow_id]
                                shadow_blocks[input_name] = shadow_id
                            elif input_name == "DISTANCETOMENU":
                                shadow_id = self._create_distance_shadow(value)
                                inputs[input_name] = [1, shadow_id]
                                shadow_blocks[input_name] = shadow_id
                            elif input_name in ["TO", "TOWARDS"]:
                                shadow_id = self._create_goto_shadow(value, input_name)
                                inputs[input_name] = [1, shadow_id]
                                shadow_blocks[input_name] = shadow_id
                            elif input_name == "OBJECT":
                                if value in ["舞台", "Stage"]:
                                    inputs[input_name] = [1, [11, TARGET_STAGE, TARGET_STAGE]]
                                else:
                                    inputs[input_name] = [1, [11, value, value]]
                            else:
                                inputs[input_name] = self._parse_value(value)
                
                if "fields" in block_def:
                    for field_name, group_idx in block_def["fields"].items():
                        if isinstance(group_idx, int):
                            value = match.group(group_idx)
                            
                            if field_name == "KEY_OPTION" and opcode == "event_whenkeypressed":
                                key = self._get_key_name(value)
                                fields[field_name] = [key, None]
                            elif field_name == "PROPERTY":
                                property_map = {
                                    "x坐标": "x position",
                                    "y坐标": "y position",
                                    "方向": "direction",
                                    "造型编号": "costume #",
                                    "造型名称": "costume name",
                                    "大小": "size",
                                    "音量": "volume",
                                    "背景编号": "backdrop #",
                                    "背景名称": "backdrop name"
                                }
                                fields[field_name] = [property_map.get(value, value), None]
                            else:
                                fields[field_name] = [value, None]
                        else:
                            fields[field_name] = group_idx
                
                block_id = self.builder.add_block(opcode, inputs, fields, parent, top_level)
                
                # 🔥 设置所有 shadow blocks 的 parent
                for shadow_id in shadow_blocks.values():
                    if shadow_id and shadow_id in self.builder.current_sprite["blocks"]:
                        self.builder.current_sprite["blocks"][shadow_id]["parent"] = block_id
                
                if parent:
                    self.builder.current_sprite["blocks"][parent]["next"] = block_id
                
                return block_id
        
        return None
    
    def _create_say_think_block(self, cmd, parent=None, top_level=False):
        """创建"说/想"积木"""
        parts = cmd.strip().split(None, 1)
        if len(parts) < 2:
            return None
        
        keyword = parts[0]
        content = parts[1].strip()
        
        duration = 2
        has_duration = False
        time_match = re.search(r'\s+([\d.]+)\s*秒\s*$', content)
        if time_match:
            has_duration = True
            duration = float(time_match.group(1))
            content = content[:time_match.start()].strip()
        
        message_input = self._parse_say_content(content)
        
        opcode_map = {"说": "looks_say", "想": "looks_think"}
        opcode = opcode_map.get(keyword, "looks_say")
        if has_duration:
            opcode += "forsecs"
        
        inputs = {"MESSAGE": message_input}
        if has_duration:
            inputs["SECS"] = [1, [4, str(duration)]]
        
        block_id = self.builder.add_block(opcode, inputs, {}, parent, top_level)
        if parent:
            self.builder.current_sprite["blocks"][parent]["next"] = block_id
        return block_id
    
    def _parse_say_content(self, content):
        """解析"说"的内容"""
        content = content.strip()
        
        join_match = re.match(r'连接\s*\((.*)\)\s*$', content)
        if join_match:
            args_str = join_match.group(1)
            args = self._split_by_comma(args_str)
            return self._build_join_chain(args)
        
        if '+' in content and not content.startswith('+'):
            parts = self._split_by_plus(content)
            return self._build_join_chain(parts)
        
        string_match = re.match(r'^["\'](.+)["\']$', content)
        if string_match:
            return [1, [10, string_match.group(1)]]
        
        return self._parse_variable_or_reporter(content)
    
    def _parse_value(self, text):
        """解析值"""
        text = text.strip()
        
        # 1. 逻辑运算符
        if ' 或 ' in text:
            parts = text.split(' 或 ', 1)
            input1 = self._parse_value(parts[0])
            input2 = self._parse_value(parts[1])
            return [2, self.builder.add_block("operator_or", {"OPERAND1": input1, "OPERAND2": input2}, {}, None, False)]
        
        if ' 且 ' in text:
            parts = text.split(' 且 ', 1)
            input1 = self._parse_value(parts[0])
            input2 = self._parse_value(parts[1])
            return [2, self.builder.add_block("operator_and", {"OPERAND1": input1, "OPERAND2": input2}, {}, None, False)]

        # 2. 比较运算符
        # 处理 >= 和 <= (Scratch 没有原生支持，需要用 not 组合实现)
        if '>=' in text:
            parts = text.split('>=', 1)
            if len(parts) == 2:
                input1 = self._parse_value(parts[0].strip())
                input2 = self._parse_value(parts[1].strip())
                # a >= b 等价于 not (a < b)
                lt_block = self.builder.add_block("operator_lt", {"OPERAND1": input1, "OPERAND2": input2}, {}, None, False)
                not_block = self.builder.add_block("operator_not", {"OPERAND": [2, lt_block]}, {}, None, False)
                return [2, not_block]

        if '<=' in text:
            parts = text.split('<=', 1)
            if len(parts) == 2:
                input1 = self._parse_value(parts[0].strip())
                input2 = self._parse_value(parts[1].strip())
                # a <= b 等价于 not (a > b)
                gt_block = self.builder.add_block("operator_gt", {"OPERAND1": input1, "OPERAND2": input2}, {}, None, False)
                not_block = self.builder.add_block("operator_not", {"OPERAND": [2, gt_block]}, {}, None, False)
                return [2, not_block]

        for op_char, op_code in [('>', 'operator_gt'), ('<', 'operator_lt'), ('=', 'operator_equals')]:
            if op_char in text:
                parts = text.split(op_char, 1)
                if len(parts) == 2:
                    input1 = self._parse_value(parts[0].strip())
                    input2 = self._parse_value(parts[1].strip())
                    return [2, self.builder.add_block(op_code, {"OPERAND1": input1, "OPERAND2": input2}, {}, None, False)]

        # 3. 连接表达式
        if ('+' in text and not text.startswith('+')) or text.startswith("连接("):
            return self._build_join_chain_from_text(text)

        # 4. 复杂 Reporter
        mod_match = re.match(r"(.+?)\s*除以\s*(.+?)\s*的余数", text)
        if mod_match:
            input1 = self._parse_value(mod_match.group(1))
            input2 = self._parse_value(mod_match.group(2))
            return [2, self.builder.add_block("operator_mod", {"NUM1": input1, "NUM2": input2}, {}, None, False)]
        
        rand_match = re.match(r"从\s*(.+?)\s*到\s*(.+?)\s*随机选一个数", text)
        if rand_match:
            input1 = self._parse_value(rand_match.group(1))
            input2 = self._parse_value(rand_match.group(2))
            return [2, self.builder.add_block("operator_random", {"FROM": input1, "TO": input2}, {}, None, False)]
            
        # 5. ~ 前缀
        if text.startswith('~'):
            return self._parse_variable_or_reporter(text)
        
        # 6. 数字
        try:
            num_val = float(text)
            return [1, [4, str(num_val)]]
        except ValueError:
            pass
        
        # 7. 字符串
        if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
            return [1, [10, text[1:-1]]]
            
        # 8. Shadow Block 触发器
        if text in self.SPECIAL_TARGETS:
            val = self.SPECIAL_TARGETS[text]
            return [1, [11, val, val]]
        
        # 9. 默认: 普通字符串
        return [1, [10, text]]
    
    def _parse_condition(self, text):
        """解析条件表达式"""
        text = text.strip()
        
        # 1. 逻辑运算符
        if ' 或 ' in text:
            parts = text.split(' 或 ', 1)
            input1 = self._parse_condition(parts[0])
            input2 = self._parse_condition(parts[1])
            return [2, self.builder.add_block("operator_or", {"OPERAND1": input1, "OPERAND2": input2}, {}, None, False)]
        
        if ' 且 ' in text:
            parts = text.split(' 且 ', 1)
            input1 = self._parse_condition(parts[0])
            input2 = self._parse_condition(parts[1])
            return [2, self.builder.add_block("operator_and", {"OPERAND1": input1, "OPERAND2": input2}, {}, None, False)]
        
        # 2. 按键判断
        key_match = re.match(r'^按下\s+(.+?)\s*键\??$', text)
        if key_match:
            key_value = key_match.group(1).strip()
            return [2, self._create_keypressed_block(key_value)]
        
        # 3. 碰到判断
        touch_match = re.match(r'^碰到\s+(.+?)\s*\??$', text)
        if touch_match:
            object_name = touch_match.group(1).strip()
            return [2, self._create_touching_block(object_name)]
        
        # 4. 鼠标按下
        if text in ['鼠标按下', '鼠标按下?']:
            return [2, self.builder.add_block("sensing_mousedown", {}, {}, None, False)]
        
        # 5. 比较运算符
        # 处理 >= 和 <= (Scratch 没有原生支持，需要用 not 组合实现)
        if '>=' in text:
            parts = text.split('>=', 1)
            if len(parts) == 2:
                input1 = self._parse_operand(parts[0].strip())
                input2 = self._parse_operand(parts[1].strip())
                # a >= b 等价于 not (a < b)
                lt_block = self.builder.add_block("operator_lt", {"OPERAND1": input1, "OPERAND2": input2}, {}, None, False)
                not_block = self.builder.add_block("operator_not", {"OPERAND": [2, lt_block]}, {}, None, False)
                return [2, not_block]

        if '<=' in text:
            parts = text.split('<=', 1)
            if len(parts) == 2:
                input1 = self._parse_operand(parts[0].strip())
                input2 = self._parse_operand(parts[1].strip())
                # a <= b 等价于 not (a > b)
                gt_block = self.builder.add_block("operator_gt", {"OPERAND1": input1, "OPERAND2": input2}, {}, None, False)
                not_block = self.builder.add_block("operator_not", {"OPERAND": [2, gt_block]}, {}, None, False)
                return [2, not_block]

        for op_char, op_code in [('>', 'operator_gt'), ('<', 'operator_lt'), ('=', 'operator_equals')]:
            if op_char in text:
                parts = text.split(op_char, 1)
                if len(parts) == 2:
                    input1 = self._parse_operand(parts[0].strip())
                    input2 = self._parse_operand(parts[1].strip())
                    return [2, self.builder.add_block(op_code, {"OPERAND1": input1, "OPERAND2": input2}, {}, None, False)]
        
        # 6. 默认
        return self._parse_value(text)
    
    def _parse_variable_or_reporter(self, text):
        """解析变量或reporter积木"""
        text = text.strip()
        
        if text.startswith('~'):
            var_or_reporter = text[1:].strip()
            
            builtin_reporters = {
                "回答": "sensing_answer",
                "x坐标": "motion_xposition",
                "y坐标": "motion_yposition",
                "方向": "motion_direction",
                "计时器": "sensing_timer",
                "响度": "sensing_loudness",
                "鼠标x坐标": "sensing_mousex",
                "鼠标y坐标": "sensing_mousey",
                "鼠标的x坐标": "sensing_mousex",
                "鼠标的y坐标": "sensing_mousey",
                "大小": "looks_size",
                "音量": "sound_volume",
            }
            
            if var_or_reporter in builtin_reporters:
                reporter_id = self.builder.add_block(
                    builtin_reporters[var_or_reporter],
                    {}, {}, None, False
                )
                return [2, reporter_id]
            
            special_reporters = {
                "造型编号": ("looks_costumenumbername", {"NUMBER_NAME": ["number", None]}),
                "造型名称": ("looks_costumenumbername", {"NUMBER_NAME": ["name", None]}),
                "背景编号": ("looks_backdropnumbername", {"NUMBER_NAME": ["number", None]}),
                "背景名称": ("looks_backdropnumbername", {"NUMBER_NAME": ["name", None]}),
            }
            
            if var_or_reporter in special_reporters:
                opcode, fields = special_reporters[var_or_reporter]
                reporter_id = self.builder.add_block(opcode, {}, fields, None, False)
                return [2, reporter_id]
            
            distance_match = re.match(r"^到\s+(.+?)\s*的距离$", var_or_reporter)
            if distance_match:
                target = distance_match.group(1).strip()
                shadow_id = self._create_distance_shadow(target)
                reporter_id = self.builder.add_block(
                    "sensing_distanceto",
                    {"DISTANCETOMENU": [1, shadow_id]},
                    {}, None, False
                )
                # 🔥 设置 shadow 的 parent
                if shadow_id and reporter_id:
                    self.builder.current_sprite["blocks"][shadow_id]["parent"] = reporter_id
                return [2, reporter_id]
            
            property_match = re.match(r"^(.+?)\s*的\s*(x坐标|y坐标|方向|造型编号|造型名称|大小|音量|背景编号|背景名称)$", var_or_reporter)
            if property_match:
                sprite_name = property_match.group(1).strip()
                prop = property_match.group(2).strip()
                
                property_map = {
                    "x坐标": "x position",
                    "y坐标": "y position",
                    "方向": "direction",
                    "造型编号": "costume #",
                    "造型名称": "costume name",
                    "大小": "size",
                    "音量": "volume",
                    "背景编号": "backdrop #",
                    "背景名称": "backdrop name"
                }
                
                obj_val = TARGET_STAGE if sprite_name == "舞台" else sprite_name
                reporter_id = self.builder.add_block(
                    "sensing_of",
                    {"OBJECT": [1, [11, obj_val, obj_val]]},
                    {"PROPERTY": [property_map[prop], None]},
                    None, False
                )
                return [2, reporter_id]
            
            return self._create_variable_block(var_or_reporter)
        
        try:
            num_value = float(text)
            return [1, [4, str(num_value)]]
        except ValueError:
            pass

        return [1, [10, text]]

    def _create_variable_block(self, var_name):
        """创建变量引用block"""
        for var_id, var_data in self.builder.current_sprite.get("variables", {}).items():
            if var_data[0] == var_name:
                reporter_id = self.builder.add_block(
                    "data_variable",
                    {}, {"VARIABLE": [var_name, var_id]},
                    None, False
                )
                return [2, reporter_id]
        
        if self.builder.stage:
            for var_id, var_data in self.builder.stage.get("variables", {}).items():
                if var_data[0] == var_name:
                    reporter_id = self.builder.add_block(
                        "data_variable",
                        {}, {"VARIABLE": [var_name, var_id]},
                        None, False
                    )
                    return [2, reporter_id]
        
        print(f"⚠️ 警告: 未定义的变量 '~{var_name}'，将作为字符串处理")
        return [1, [10, var_name]]
    
    def _parse_operand(self, text):
        """解析操作数"""
        text = text.strip()

        if text.startswith('~'):
            return self._parse_variable_or_reporter(text)

        try:
            num_value = float(text)
            return [1, [4, str(num_value)]]
        except ValueError:
            pass

        return [1, [10, text]]
    
    def _create_keypressed_block(self, key_value):
        """创建"按下键"判断block"""
        shadow_id = self._create_key_shadow(key_value)
        block_id = self.builder.add_block(
            "sensing_keypressed",
            {"KEY_OPTION": [1, shadow_id]},
            {}, None, False
        )
        # 🔥 设置 shadow 的 parent
        if shadow_id and block_id:
            self.builder.current_sprite["blocks"][shadow_id]["parent"] = block_id
        return block_id
    
    def _create_touching_block(self, object_name):
        """创建"碰到"判断block"""
        shadow_id = self._create_touching_shadow(object_name)
        block_id = self.builder.add_block(
            "sensing_touchingobject",
            {"TOUCHINGOBJECTMENU": [1, shadow_id]},
            {}, None, False
        )
        # 🔥 设置 shadow 的 parent
        if shadow_id and block_id:
            self.builder.current_sprite["blocks"][shadow_id]["parent"] = block_id
        return block_id
    
    def _build_join_chain_from_text(self, content):
        """从文本构建连接链"""
        if content.startswith("连接(") and content.endswith(")"):
            inner = content[3:-1]
            parts = self._split_by_comma(inner)
        else:
            parts = self._split_by_plus(content)
        
        return self._build_join_chain(parts)
    
    def _build_join_chain(self, parts):
        """构建join积木链（递归）"""
        if len(parts) == 0:
            return [1, [10, ""]]
        elif len(parts) == 1:
            return self._parse_say_part(parts[0])
        else:
            left_part = self._parse_say_part(parts[0])
            right_part = self._build_join_chain(parts[1:])
            join_id = self.builder.add_block(
                "operator_join",
                {"STRING1": left_part, "STRING2": right_part},
                {}, None, False
            )
            return [2, join_id]
    
    def _split_by_delimiter(self, text, delimiter):
        """按指定分隔符分割（保留引号和括号内的内容）"""
        parts = []
        current = ""
        in_quotes = False
        quote_char = None
        paren_depth = 0

        for char in text:
            if char in ['"', "'"]:
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                current += char
            elif not in_quotes:
                if char == '(':
                    paren_depth += 1
                elif char == ')':
                    paren_depth -= 1

                if char == delimiter and paren_depth == 0:
                    if current.strip():
                        parts.append(current.strip())
                    current = ""
                else:
                    current += char
            else:
                current += char

        if current.strip():
            parts.append(current.strip())

        return [p for p in parts if p]

    def _split_by_plus(self, text):
        """按 + 分割（保留引号内的内容）"""
        return self._split_by_delimiter(text, '+')

    def _split_by_comma(self, text):
        """按逗号分割（保留引号内的逗号）"""
        return self._split_by_delimiter(text, ',')
    
    def _parse_say_part(self, part):
        """解析"说"内容的单个部分"""
        part = part.strip()
        
        string_match = re.match(r'^["\'](.+)["\']$', part)
        if string_match:
            return [1, [10, string_match.group(1)]]
        
        return self._parse_variable_or_reporter(part)
    
    def _get_key_name(self, value):
        # 1. 先查表（包括"上"、"↑"等）
        if value in self.KEY_MAP:
            return self.KEY_MAP[value]  # "上" → "up arrow" ✅
        
        # 2. 不在表中，如果是单字符，当作字母键
        if len(value) == 1:
            return value.lower()  # "a" → "a" ✅
        
        # 3. 其他情况
        return value.lower()
    
    def _create_key_shadow(self, value):
        """创建按键选择的 shadow block"""
        key = self._get_key_name(value)
        shadow_id = self.builder.add_shadow_block(
            "sensing_keyoptions",
            {"KEY_OPTION": [key, None]}
        )
        return shadow_id
    
    def _create_touching_shadow(self, value):
        """创建碰到对象的 shadow block"""
        obj = self.SPECIAL_TARGETS.get(value, value)
        shadow_id = self.builder.add_shadow_block(
            "sensing_touchingobjectmenu",
            {"TOUCHINGOBJECTMENU": [obj, None]}
        )
        return shadow_id
    
    def _create_distance_shadow(self, value):
        """创建距离目标的 shadow block"""
        obj = self.SPECIAL_TARGETS.get(value, value)
        shadow_id = self.builder.add_shadow_block(
            "sensing_distancetomenu",
            {"DISTANCETOMENU": [obj, None]}
        )
        return shadow_id
    
    def _create_goto_shadow(self, value, input_type):
        """创建移到/面向目标的 shadow block"""
        obj = self.SPECIAL_TARGETS.get(value, value)
        
        if input_type == "TO":
            shadow_opcode = "motion_goto_menu"
            field_name = "TO"
        else:
            shadow_opcode = "motion_pointtowards_menu"
            field_name = "TOWARDS"
        
        shadow_id = self.builder.add_shadow_block(
            shadow_opcode,
            {field_name: [obj, None]}
        )
        return shadow_id
    
    def compile(self, output_file):
        """编译并保存"""
        self.builder.save(output_file)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python parser.py <输入文件.sl> [-o 输出文件.sb3]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[3] if len(sys.argv) > 3 else "output.sb3"
    
    parser = ScratchLangParser()
    parser.parse_file(input_file)
    parser.compile(output_file)
    print(f"✅ 编译成功: {output_file}")