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

try:
    from .exceptions import ParseError, CompileError
except ImportError:
    # 当作为脚本直接运行时
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from compiler.exceptions import ParseError, CompileError

class SB3Decompiler:
    """Scratch 3.0 项目反编译器"""

    def __init__(self):
        self.project = None
        self.sl_code = []

    def load_sb3(self, filepath: str) -> Dict[str, Any]:
        """加载 sb3 文件"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")

        if not filepath.lower().endswith('.sb3'):
            raise ParseError(f"文件格式错误，必须是 .sb3 文件: {filepath}")

        try:
            with zipfile.ZipFile(filepath, 'r') as zf:
                if 'project.json' not in zf.namelist():
                    raise ParseError(f"无效的 .sb3 文件，缺少 project.json: {filepath}")

                project_json = zf.read('project.json').decode('utf-8')
                self.project = json.loads(project_json)
        except zipfile.BadZipFile:
            raise ParseError(f"无效的 ZIP 文件: {filepath}")
        except json.JSONDecodeError as e:
            raise ParseError(f"project.json 格式错误: {e}")
        except ParseError:
            # 重新抛出 ParseError
            raise
        except Exception as e:
            raise CompileError(f"加载 .sb3 文件时发生错误: {e}")

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

        # 处理自定义积木定义
        blocks = target.get('blocks', {})
        self._process_custom_blocks(blocks)

        self.sl_code.append("")

        # 处理脚本
        self._process_scripts(blocks)

        self.sl_code.append("")

    def _process_custom_blocks(self, blocks: Dict[str, Any]):
        """处理自定义积木定义"""
        for block_id, block in blocks.items():
            if isinstance(block, dict) and block.get('opcode') == 'procedures_definition':
                # 获取自定义积木的原型
                prototype_id = block.get('inputs', {}).get('custom_block', [None, None])[1]
                if prototype_id:
                    prototype = blocks.get(prototype_id)
                    if prototype:
                        proccode = prototype.get('mutation', {}).get('proccode', '')
                        if proccode:
                            self.sl_code.append(f"// 自定义积木定义: {proccode}")

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
        elif opcode == 'event_whenkeypressed':
            key = self._get_field_value(block, 'KEY_OPTION')
            return f"当按下 {key} 键"
        elif opcode == 'event_whenthisspriteclicked':
            return "当角色被点击"
        elif opcode == 'event_whenstageclicked':
            return "当舞台被点击"
        elif opcode == 'event_whenbroadcastreceived':
            msg = self._get_field_value(block, 'BROADCAST_OPTION')
            return f"当收到 {msg}"
        elif opcode == 'event_whenbackdropswitchesto':
            backdrop = self._get_field_value(block, 'BACKDROP')
            return f"当背景换成 {backdrop}"

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
        elif opcode == 'motion_goto':
            to = self._get_input_value(blocks, block, 'TO')
            return f"移到 {to}"
        elif opcode == 'motion_gotoxy':
            x = self._get_input_value(blocks, block, 'X')
            y = self._get_input_value(blocks, block, 'Y')
            return f"移到 {x} {y}"
        elif opcode == 'motion_glideto':
            secs = self._get_input_value(blocks, block, 'SECS')
            to = self._get_input_value(blocks, block, 'TO')
            return f"滑行 {secs} 秒到 {to}"
        elif opcode == 'motion_glidesecstoxy':
            secs = self._get_input_value(blocks, block, 'SECS')
            x = self._get_input_value(blocks, block, 'X')
            y = self._get_input_value(blocks, block, 'Y')
            return f"滑行 {secs} 秒到 {x} {y}"
        elif opcode == 'motion_pointindirection':
            direction = self._get_input_value(blocks, block, 'DIRECTION')
            return f"面向 {direction} 方向"
        elif opcode == 'motion_pointtowards':
            towards = self._get_input_value(blocks, block, 'TOWARDS')
            return f"面向 {towards}"
        elif opcode == 'motion_changexby':
            dx = self._get_input_value(blocks, block, 'DX')
            return f"将x坐标增加 {dx}"
        elif opcode == 'motion_setx':
            x = self._get_input_value(blocks, block, 'X')
            return f"将x坐标设为 {x}"
        elif opcode == 'motion_changeyby':
            dy = self._get_input_value(blocks, block, 'DY')
            return f"将y坐标增加 {dy}"
        elif opcode == 'motion_sety':
            y = self._get_input_value(blocks, block, 'Y')
            return f"将y坐标设为 {y}"
        elif opcode == 'motion_ifonedgebounce':
            return "碰到边缘就反弹"
        elif opcode == 'motion_setrotationstyle':
            style = self._get_field_value(block, 'STYLE')
            return f"将旋转方式设为 {style}"

        # 外观块
        elif opcode == 'looks_say':
            message = self._get_input_value(blocks, block, 'MESSAGE')
            return f"说 {message}"
        elif opcode == 'looks_sayforsecs':
            message = self._get_input_value(blocks, block, 'MESSAGE')
            secs = self._get_input_value(blocks, block, 'SECS')
            return f"说 {message} {secs}秒"
        elif opcode == 'looks_think':
            message = self._get_input_value(blocks, block, 'MESSAGE')
            return f"想 {message}"
        elif opcode == 'looks_thinkforsecs':
            message = self._get_input_value(blocks, block, 'MESSAGE')
            secs = self._get_input_value(blocks, block, 'SECS')
            return f"想 {message} {secs}秒"
        elif opcode == 'looks_switchcostumeto':
            costume = self._get_input_value(blocks, block, 'COSTUME')
            return f"切换造型到 {costume}"
        elif opcode == 'looks_nextcostume':
            return "下一个造型"
        elif opcode == 'looks_switchbackdropto':
            backdrop = self._get_input_value(blocks, block, 'BACKDROP')
            return f"切换背景到 {backdrop}"
        elif opcode == 'looks_nextbackdrop':
            return "下一个背景"
        elif opcode == 'looks_changesizeby':
            change = self._get_input_value(blocks, block, 'CHANGE')
            return f"将大小增加 {change}"
        elif opcode == 'looks_setsizeto':
            size = self._get_input_value(blocks, block, 'SIZE')
            return f"将大小设为 {size}"
        elif opcode == 'looks_changeeffectby':
            effect = self._get_field_value(block, 'EFFECT')
            change = self._get_input_value(blocks, block, 'CHANGE')
            return f"将 {effect} 特效增加 {change}"
        elif opcode == 'looks_seteffectto':
            effect = self._get_field_value(block, 'EFFECT')
            value = self._get_input_value(blocks, block, 'VALUE')
            return f"将 {effect} 特效设为 {value}"
        elif opcode == 'looks_cleargraphiceffects':
            return "清除图形特效"
        elif opcode == 'looks_show':
            return "显示"
        elif opcode == 'looks_hide':
            return "隐藏"
        elif opcode == 'looks_gotofrontback':
            front_back = self._get_field_value(block, 'FRONT_BACK')
            return f"移到最{front_back}层"
        elif opcode == 'looks_goforwardbackwardlayers':
            forward_backward = self._get_field_value(block, 'FORWARD_BACKWARD')
            num = self._get_input_value(blocks, block, 'NUM')
            return f"图层{forward_backward} {num}"

        # 声音块
        elif opcode == 'sound_play':
            sound = self._get_input_value(blocks, block, 'SOUND_MENU')
            return f"播放声音 {sound}"
        elif opcode == 'sound_playuntildone':
            sound = self._get_input_value(blocks, block, 'SOUND_MENU')
            return f"播放声音 {sound} 直到结束"
        elif opcode == 'sound_stopallsounds':
            return "停止所有声音"
        elif opcode == 'sound_changevolumeby':
            volume = self._get_input_value(blocks, block, 'VOLUME')
            return f"将音量增加 {volume}"
        elif opcode == 'sound_setvolumeto':
            volume = self._get_input_value(blocks, block, 'VOLUME')
            return f"将音量设为 {volume}"
        elif opcode == 'sound_changeeffectby':
            effect = self._get_field_value(block, 'EFFECT')
            value = self._get_input_value(blocks, block, 'VALUE')
            return f"将 {effect} 音效增加 {value}"
        elif opcode == 'sound_seteffectto':
            effect = self._get_field_value(block, 'EFFECT')
            value = self._get_input_value(blocks, block, 'VALUE')
            return f"将 {effect} 音效设为 {value}"
        elif opcode == 'sound_cleareffects':
            return "清除声音特效"

        # 控制块
        elif opcode == 'control_wait':
            duration = self._get_input_value(blocks, block, 'DURATION')
            return f"等待 {duration} 秒"
        elif opcode == 'control_repeat':
            times = self._get_input_value(blocks, block, 'TIMES')
            return f"重复 {times} 次"
        elif opcode == 'control_forever':
            return "重复执行"
        elif opcode == 'control_if':
            condition = self._get_input_value(blocks, block, 'CONDITION')
            return f"如果 {condition} 那么"
        elif opcode == 'control_if_else':
            condition = self._get_input_value(blocks, block, 'CONDITION')
            return f"如果 {condition} 那么"
        elif opcode == 'control_waituntil':
            condition = self._get_input_value(blocks, block, 'CONDITION')
            return f"等待直到 {condition}"
        elif opcode == 'control_repeat_until':
            condition = self._get_input_value(blocks, block, 'CONDITION')
            return f"重复执行直到 {condition}"
        elif opcode == 'control_stop':
            stop_option = self._get_field_value(block, 'STOP_OPTION')
            return f"停止 {stop_option}"
        elif opcode == 'control_create_clone_of':
            clone_option = self._get_input_value(blocks, block, 'CLONE_OPTION')
            return f"克隆 {clone_option}"
        elif opcode == 'control_delete_this_clone':
            return "删除此克隆体"
        elif opcode == 'control_start_as_clone':
            return "当作为克隆体启动时"

        # 事件块 - 添加广播支持
        elif opcode == 'event_broadcast':
            broadcast_input = self._get_input_value(blocks, block, 'BROADCAST_INPUT')
            return f"广播 {broadcast_input}"
        elif opcode == 'event_broadcastandwait':
            broadcast_input = self._get_input_value(blocks, block, 'BROADCAST_INPUT')
            return f"广播 {broadcast_input} 并等待"

        # 侦测块
        elif opcode == 'sensing_touchingobject':
            touchingobjectmenu = self._get_input_value(blocks, block, 'TOUCHINGOBJECTMENU')
            return f"碰到 {touchingobjectmenu}"
        elif opcode == 'sensing_askandwait':
            question = self._get_input_value(blocks, block, 'QUESTION')
            return f"询问 {question} 并等待"
        elif opcode == 'sensing_resettimer':
            return "计时器归零"
        elif opcode == 'sensing_setdragmode':
            drag_mode = self._get_field_value(block, 'DRAG_MODE')
            return f"设置拖动模式为 {drag_mode}"

        # 运算块（报告块，不应该单独出现）
        elif opcode.startswith('operator_'):
            return None  # 运算块应该在表达式中处理

        # 变量块
        elif opcode == 'data_setvariableto':
            var_name = self._get_field_value(block, 'VARIABLE')
            value = self._get_input_value(blocks, block, 'VALUE')
            return f"设置 ~{var_name} 为 {value}"
        elif opcode == 'data_changevariableby':
            var_name = self._get_field_value(block, 'VARIABLE')
            value = self._get_input_value(blocks, block, 'VALUE')
            return f"将 ~{var_name} 增加 {value}"
        elif opcode == 'data_showvariable':
            var_name = self._get_field_value(block, 'VARIABLE')
            return f"显示变量 ~{var_name}"
        elif opcode == 'data_hidevariable':
            var_name = self._get_field_value(block, 'VARIABLE')
            return f"隐藏变量 ~{var_name}"

        # 列表块
        elif opcode == 'data_addtolist':
            item = self._get_input_value(blocks, block, 'ITEM')
            list_name = self._get_field_value(block, 'LIST')
            return f"将 {item} 加入 {list_name}"
        elif opcode == 'data_deleteoflist':
            index = self._get_input_value(blocks, block, 'INDEX')
            list_name = self._get_field_value(block, 'LIST')
            return f"删除 {list_name} 的第 {index} 项"
        elif opcode == 'data_deletealloflist':
            list_name = self._get_field_value(block, 'LIST')
            return f"删除 {list_name} 的全部项目"
        elif opcode == 'data_insertatlist':
            item = self._get_input_value(blocks, block, 'ITEM')
            index = self._get_input_value(blocks, block, 'INDEX')
            list_name = self._get_field_value(block, 'LIST')
            return f"将 {item} 插入 {list_name} 的第 {index} 项"
        elif opcode == 'data_replaceitemoflist':
            index = self._get_input_value(blocks, block, 'INDEX')
            item = self._get_input_value(blocks, block, 'ITEM')
            list_name = self._get_field_value(block, 'LIST')
            return f"将 {list_name} 的第 {index} 项替换为 {item}"

        # 画笔块
        elif opcode == 'pen_clear':
            return "清空"
        elif opcode == 'pen_stamp':
            return "图章"
        elif opcode == 'pen_penDown':
            return "落笔"
        elif opcode == 'pen_penUp':
            return "抬笔"
        elif opcode == 'pen_setPenColorToColor':
            color = self._get_input_value(blocks, block, 'COLOR')
            return f"将笔的颜色设为 {color}"
        elif opcode == 'pen_changePenColorParamBy':
            param = self._get_field_value(block, 'colorParam')
            value = self._get_input_value(blocks, block, 'VALUE')
            return f"将笔的 {param} 增加 {value}"
        elif opcode == 'pen_setPenColorParamTo':
            param = self._get_field_value(block, 'colorParam')
            value = self._get_input_value(blocks, block, 'VALUE')
            return f"将笔的 {param} 设为 {value}"
        elif opcode == 'pen_changePenSizeBy':
            size = self._get_input_value(blocks, block, 'SIZE')
            return f"将笔的粗细增加 {size}"
        elif opcode == 'pen_setPenSizeTo':
            size = self._get_input_value(blocks, block, 'SIZE')
            return f"将笔的粗细设为 {size}"

        # 音乐块
        elif opcode == 'music_playDrumForBeats':
            drum = self._get_input_value(blocks, block, 'DRUM')
            beats = self._get_input_value(blocks, block, 'BEATS')
            return f"演奏鼓声 {drum} {beats} 拍"
        elif opcode == 'music_restForBeats':
            beats = self._get_input_value(blocks, block, 'BEATS')
            return f"休止 {beats} 拍"
        elif opcode == 'music_playNoteForBeats':
            note = self._get_input_value(blocks, block, 'NOTE')
            beats = self._get_input_value(blocks, block, 'BEATS')
            return f"演奏音符 {note} {beats} 拍"
        elif opcode == 'music_setInstrument':
            instrument = self._get_input_value(blocks, block, 'INSTRUMENT')
            return f"将乐器设为 {instrument}"
        elif opcode == 'music_setTempo':
            tempo = self._get_input_value(blocks, block, 'TEMPO')
            return f"将节奏设为 {tempo}"
        elif opcode == 'music_changeTempo':
            tempo = self._get_input_value(blocks, block, 'TEMPO')
            return f"将节奏增加 {tempo}"

        # 自定义积木
        elif opcode == 'procedures_call':
            mutation = block.get('mutation', {})
            proccode = mutation.get('proccode', '')
            if proccode:
                # 处理自定义积木的参数
                argumentids = mutation.get('argumentids', '[]')
                if argumentids != '[]':
                    try:
                        import json
                        arg_ids = json.loads(argumentids)
                        args = []
                        for arg_id in arg_ids:
                            arg_value = self._get_input_value(blocks, block, arg_id)
                            args.append(arg_value)
                        return f"{proccode} {' '.join(args)}"
                    except:
                        pass
                return proccode
            return f"// 自定义积木调用: {block_id}"

        # 扩展积木 - 通用处理
        elif '_' in opcode and not opcode.startswith(('event_', 'motion_', 'looks_', 'sound_', 'control_', 'sensing_', 'operator_', 'data_', 'pen_', 'music_')):
            # 这可能是扩展积木
            extension_name = opcode.split('_')[0]
            block_name = '_'.join(opcode.split('_')[1:])

            # 尝试获取所有输入参数
            inputs = block.get('inputs', {})
            fields = block.get('fields', {})

            params = []
            for input_name, input_data in inputs.items():
                value = self._get_input_value(blocks, block, input_name)
                params.append(value)

            for field_name, field_data in fields.items():
                value = self._get_field_value(block, field_name)
                params.append(value)

            param_str = ' '.join(params) if params else ''
            return f"// 扩展积木 [{extension_name}]: {block_name} {param_str}".strip()

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
                    if value_type == 4:  # 数字（整数）
                        return str(value)
                    elif value_type == 5:  # 数字（浮点数）
                        return str(value)
                    elif value_type == 6:  # 正整数
                        return str(value)
                    elif value_type == 7:  # 正数
                        return str(value)
                    elif value_type == 8:  # 整数
                        return str(value)
                    elif value_type == 9:  # 角度
                        return str(value)
                    elif value_type == 10:  # 字符串
                        return f'"{value}"'
                    elif value_type == 11:  # 广播消息
                        return f'"{value}"'
                    elif value_type == 12:  # 变量
                        return f"~{value}"
                    elif value_type == 13:  # 列表
                        return f"~{value}"
                # 处理 input_type == 1 但 input_value 是字符串的情况（菜单块引用）
                elif isinstance(input_value, str):
                    ref_block = blocks.get(input_value)
                    if ref_block:
                        return self._convert_reporter_block(blocks, ref_block)

            # 块引用 (input_type == 2 或 3)
            elif input_type in [2, 3]:
                if isinstance(input_value, str):
                    ref_block = blocks.get(input_value)
                    if ref_block:
                        return self._convert_reporter_block(blocks, ref_block)
                # 处理 input_type == 3 且 input_value 是列表的情况（变量引用）
                elif isinstance(input_value, list) and len(input_value) >= 2:
                    value_type = input_value[0]
                    if value_type == 12:  # 变量引用
                        var_name = input_value[1]
                        return f"~{var_name}"
                    elif value_type == 13:  # 列表引用
                        list_name = input_value[1]
                        return f"~{list_name}"

            # 块引用 (直接字符串)
            elif isinstance(input_value, str):
                ref_block = blocks.get(input_value)
                if ref_block:
                    return self._convert_reporter_block(blocks, ref_block)

            # 菜单选项 (shadow block)
            elif isinstance(input_value, list) and len(input_value) >= 2:
                shadow_type = input_value[0]
                shadow_value = input_value[1]
                if isinstance(shadow_value, str):
                    shadow_block = blocks.get(shadow_value)
                    if shadow_block:
                        # 处理菜单块
                        shadow_opcode = shadow_block.get('opcode', '')
                        if shadow_opcode.endswith('_menu') or shadow_opcode.endswith('menu'):
                            field_name = list(shadow_block.get('fields', {}).keys())
                            if field_name:
                                return self._get_field_value(shadow_block, field_name[0])
                        return self._convert_reporter_block(blocks, shadow_block)

        return "?"

    def _convert_reporter_block(self, blocks: Dict[str, Any], block: Dict[str, Any]) -> str:
        """转换报告块"""
        opcode = block.get('opcode', '')

        # 变量和列表
        if opcode == 'data_variable':
            var_name = self._get_field_value(block, 'VARIABLE')
            return f"~{var_name}"
        elif opcode == 'data_listcontents':
            list_name = self._get_field_value(block, 'LIST')
            return f"~{list_name}"
        elif opcode == 'data_itemoflist':
            index = self._get_input_value(blocks, block, 'INDEX')
            list_name = self._get_field_value(block, 'LIST')
            return f"~{list_name} 的第 {index} 项"
        elif opcode == 'data_lengthoflist':
            list_name = self._get_field_value(block, 'LIST')
            return f"~{list_name} 的长度"
        elif opcode == 'data_listcontainsitem':
            list_name = self._get_field_value(block, 'LIST')
            item = self._get_input_value(blocks, block, 'ITEM')
            return f"~{list_name} 包含 {item}"

        # 数学运算
        elif opcode == 'operator_add':
            num1 = self._get_input_value(blocks, block, 'NUM1')
            num2 = self._get_input_value(blocks, block, 'NUM2')
            return f"({num1} + {num2})"
        elif opcode == 'operator_subtract':
            num1 = self._get_input_value(blocks, block, 'NUM1')
            num2 = self._get_input_value(blocks, block, 'NUM2')
            return f"({num1} - {num2})"
        elif opcode == 'operator_multiply':
            num1 = self._get_input_value(blocks, block, 'NUM1')
            num2 = self._get_input_value(blocks, block, 'NUM2')
            return f"({num1} * {num2})"
        elif opcode == 'operator_divide':
            num1 = self._get_input_value(blocks, block, 'NUM1')
            num2 = self._get_input_value(blocks, block, 'NUM2')
            return f"({num1} / {num2})"
        elif opcode == 'operator_random':
            from_val = self._get_input_value(blocks, block, 'FROM')
            to_val = self._get_input_value(blocks, block, 'TO')
            return f"在 {from_val} 到 {to_val} 间取随机数"
        elif opcode == 'operator_mod':
            num1 = self._get_input_value(blocks, block, 'NUM1')
            num2 = self._get_input_value(blocks, block, 'NUM2')
            return f"({num1} mod {num2})"
        elif opcode == 'operator_round':
            num = self._get_input_value(blocks, block, 'NUM')
            return f"四舍五入 {num}"
        elif opcode == 'operator_mathop':
            operator = self._get_field_value(block, 'OPERATOR')
            num = self._get_input_value(blocks, block, 'NUM')
            return f"{operator} {num}"

        # 比较运算
        elif opcode == 'operator_gt':
            operand1 = self._get_input_value(blocks, block, 'OPERAND1')
            operand2 = self._get_input_value(blocks, block, 'OPERAND2')
            return f"({operand1} > {operand2})"
        elif opcode == 'operator_lt':
            operand1 = self._get_input_value(blocks, block, 'OPERAND1')
            operand2 = self._get_input_value(blocks, block, 'OPERAND2')
            return f"({operand1} < {operand2})"
        elif opcode == 'operator_equals':
            operand1 = self._get_input_value(blocks, block, 'OPERAND1')
            operand2 = self._get_input_value(blocks, block, 'OPERAND2')
            return f"({operand1} = {operand2})"

        # 逻辑运算
        elif opcode == 'operator_and':
            operand1 = self._get_input_value(blocks, block, 'OPERAND1')
            operand2 = self._get_input_value(blocks, block, 'OPERAND2')
            return f"({operand1} 且 {operand2})"
        elif opcode == 'operator_or':
            operand1 = self._get_input_value(blocks, block, 'OPERAND1')
            operand2 = self._get_input_value(blocks, block, 'OPERAND2')
            return f"({operand1} 或 {operand2})"
        elif opcode == 'operator_not':
            operand = self._get_input_value(blocks, block, 'OPERAND')
            return f"(非 {operand})"

        # 字符串运算
        elif opcode == 'operator_join':
            string1 = self._get_input_value(blocks, block, 'STRING1')
            string2 = self._get_input_value(blocks, block, 'STRING2')
            return f"连接 {string1} 和 {string2}"
        elif opcode == 'operator_letter_of':
            letter = self._get_input_value(blocks, block, 'LETTER')
            string = self._get_input_value(blocks, block, 'STRING')
            return f"{string} 的第 {letter} 个字符"
        elif opcode == 'operator_length':
            string = self._get_input_value(blocks, block, 'STRING')
            return f"{string} 的长度"
        elif opcode == 'operator_contains':
            string1 = self._get_input_value(blocks, block, 'STRING1')
            string2 = self._get_input_value(blocks, block, 'STRING2')
            return f"{string1} 包含 {string2}"

        # 动作相关报告块
        elif opcode == 'motion_xposition':
            return "x坐标"
        elif opcode == 'motion_yposition':
            return "y坐标"
        elif opcode == 'motion_direction':
            return "方向"

        # 外观相关报告块
        elif opcode == 'looks_costumenumbername':
            number_name = self._get_field_value(block, 'NUMBER_NAME')
            return f"造型{number_name}"
        elif opcode == 'looks_backdropnumbername':
            number_name = self._get_field_value(block, 'NUMBER_NAME')
            return f"背景{number_name}"
        elif opcode == 'looks_size':
            return "大小"

        # 声音相关报告块
        elif opcode == 'sound_volume':
            return "音量"

        # 侦测相关报告块
        elif opcode == 'sensing_touchingobject':
            touchingobjectmenu = self._get_input_value(blocks, block, 'TOUCHINGOBJECTMENU')
            return f"碰到 {touchingobjectmenu}"
        elif opcode == 'sensing_touchingcolor':
            color = self._get_input_value(blocks, block, 'COLOR')
            return f"碰到颜色 {color}"
        elif opcode == 'sensing_coloristouchingcolor':
            color = self._get_input_value(blocks, block, 'COLOR')
            color2 = self._get_input_value(blocks, block, 'COLOR2')
            return f"颜色 {color} 碰到 {color2}"
        elif opcode == 'sensing_distanceto':
            distancetomenu = self._get_input_value(blocks, block, 'DISTANCETOMENU')
            return f"到 {distancetomenu} 的距离"
        elif opcode == 'sensing_answer':
            return "回答"
        elif opcode == 'sensing_keypressed':
            key_option = self._get_input_value(blocks, block, 'KEY_OPTION')
            return f"按下 {key_option} 键"
        elif opcode == 'sensing_mousedown':
            return "鼠标被按下"
        elif opcode == 'sensing_mousex':
            return "鼠标的x坐标"
        elif opcode == 'sensing_mousey':
            return "鼠标的y坐标"
        elif opcode == 'sensing_loudness':
            return "响度"
        elif opcode == 'sensing_timer':
            return "计时器"
        elif opcode == 'sensing_of':
            property_val = self._get_field_value(block, 'PROPERTY')
            object_val = self._get_input_value(blocks, block, 'OBJECT')
            return f"{object_val} 的 {property_val}"
        elif opcode == 'sensing_current':
            currentmenu = self._get_field_value(block, 'CURRENTMENU')
            return f"当前 {currentmenu}"
        elif opcode == 'sensing_dayssince2000':
            return "2000年至今的天数"
        elif opcode == 'sensing_username':
            return "用户名"

        # 菜单块处理 - 改进版
        elif opcode.endswith('_menu') or opcode.endswith('menu'):
            # 获取菜单的第一个字段值
            fields = block.get('fields', {})
            if fields:
                field_name = list(fields.keys())[0]
                field_value = self._get_field_value(block, field_name)

                # 处理特殊的菜单值
                if field_value == "_myself_":
                    return "自己"
                elif field_value == "_stage_":
                    return "舞台"
                elif field_value == "_mouse_":
                    return "鼠标指针"
                elif field_value == "_edge_":
                    return "边缘"
                elif field_value == "_random_":
                    return "随机位置"
                elif field_value == "paddle":
                    return "paddle"
                elif field_value == "ball":
                    return "ball"
                elif field_value == "deathLine":
                    return "deathLine"
                else:
                    return field_value

        return f"[{opcode}]"

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
    output_file = input_file.replace('.sb3', '.sl')
    if len(sys.argv) > 3 and sys.argv[2] == "-o":
        output_file = sys.argv[3]

    try:
        decompiler = SB3Decompiler()
        decompiler.decompile(input_file, output_file)
        print(f"反编译成功: {output_file}")
    except Exception as e:
        print(f"反编译失败: {e}")
        sys.exit(1)
