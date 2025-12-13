"""
所有Scratch积木的定义
"""
from typing import Dict, Any, Union, List, Optional

# 积木定义类型
BlockDef = Dict[str, Any]
BlocksDict = Dict[str, BlockDef]


class BlockDefinitions:
    """积木定义字典"""
    
    # ==================== 事件积木 ====================
    EVENTS = {
        "当绿旗被点击": {
            "opcode": "event_whenflagclicked",
            "pattern": r"当绿旗被点击|when flag clicked",
        },
        "当按下键": {
            "opcode": "event_whenkeypressed",
            "pattern": r"当按下\s+(.+?)\s*键",
            "fields": {"KEY_OPTION": 1}
        },
        "当角色被点击": {
            "opcode": "event_whenthisspriteclicked",
            "pattern": r"当角色被点击|when this sprite clicked"
        },
        "当舞台被点击": {
            "opcode": "event_whenstageclicked",
            "pattern": r"当舞台被点击|when stage clicked"
        },
        "当收到": {
            "opcode": "event_whenbroadcastreceived",
            "pattern": r"当收到\s+(.+)",
            "fields": {"BROADCAST_OPTION": 1}
        },
        "当背景换成": {
            "opcode": "event_whenbackdropswitchesto",
            "pattern": r"当背景换成\s+(.+)",
            "fields": {"BACKDROP": 1}
        },
    }
    
    # ==================== 动作积木 ====================
    MOTION = {
        "移动步": {
            "opcode": "motion_movesteps",
            "pattern": r"移动\s+(.+)\s*步",  # 🔥 改为 .+ 并在末尾加 \s*
            "inputs": {"STEPS": 1}
        },
        "旋转右": {
            "opcode": "motion_turnright",
            "pattern": r"旋转右\s+(.+)\s*度",
            "inputs": {"DEGREES": 1}
        },
        "旋转左": {
            "opcode": "motion_turnleft",
            "pattern": r"旋转左\s+(.+)\s*度",
            "inputs": {"DEGREES": 1}
        },
        "移到xy": {
            "opcode": "motion_gotoxy",
            "pattern": r"移到\s+(.+?)\s+(.+?)$",  # 🔥 两个参数，最后一个用 $
            "inputs": {"X": 1, "Y": 2}
        },
        "移到目标": {
            "opcode": "motion_goto",
            "pattern": r"移到\s+(.+)$",  # 🔥 匹配到行尾
            "inputs": {"TO": 1}
        },
        "面向方向": {
            "opcode": "motion_pointindirection",
            "pattern": r"面向\s+(.+)\s*方向",
            "inputs": {"DIRECTION": 1}
        },
        "面向目标": {
            "opcode": "motion_pointtowards",
            "pattern": r"面向\s+(.+)$",
            "inputs": {"TOWARDS": 1}
        },
        "滑行xy": {
            "opcode": "motion_glidesecstoxy",
            "pattern": r"在\s+(.+?)\s*秒内滑行到\s+(.+?)\s+(.+?)$",
            "inputs": {"SECS": 1, "X": 2, "Y": 3}
        },
        "滑行到目标": {
            "opcode": "motion_glideto",
            "pattern": r"在\s+(.+?)\s*秒内滑行到\s+(.+)$",
            "inputs": {"SECS": 1, "TO": 2}
        },
        "x增加": {
            "opcode": "motion_changexby",
            "pattern": r"将x坐标增加\s+(.+)$",  # 🔥 改为贪婪匹配到行尾
            "inputs": {"DX": 1}
        },
        "x设为": {
            "opcode": "motion_setx",
            "pattern": r"将x坐标设为\s+(.+)$",
            "inputs": {"X": 1}
        },
        "y增加": {
            "opcode": "motion_changeyby",
            "pattern": r"将y坐标增加\s+(.+)$",
            "inputs": {"DY": 1}
        },
        "y设为": {
            "opcode": "motion_sety",
            "pattern": r"将y坐标设为\s+(.+)$",
            "inputs": {"Y": 1}
        },
        "碰到边缘反弹": {
            "opcode": "motion_ifonedgebounce",
            "pattern": r"碰到边缘就反弹"
        },
        "设置旋转方式": {
            "opcode": "motion_setrotationstyle",
            "pattern": r"将旋转方式设为\s+(.+)",
            "fields": {"STYLE": 1}
        },
    }
    
    # ==================== 外观积木 ====================
    LOOKS = {
        "想秒": {
            "opcode": "looks_thinkforsecs",
            "pattern": r'想\s+(.+?)\s+([\d.]+)\s*秒',
            "inputs": {"MESSAGE": 1, "SECS": 2}
        },
        "想": {
            "opcode": "looks_think",
            "pattern": r'想\s+(.+?)(?:\s|$)',
            "inputs": {"MESSAGE": 1}
        },
        "切换造型": {
            "opcode": "looks_switchcostumeto",
            "pattern": r"切换造型到\s+(.+)",
            "inputs": {"COSTUME": 1}
        },
        "下一个造型": {
            "opcode": "looks_nextcostume",
            "pattern": r"下一个造型"
        },
        "切换背景": {
            "opcode": "looks_switchbackdropto",
            "pattern": r"切换背景到\s+(.+)",
            "inputs": {"BACKDROP": 1}
        },
        "下一个背景": {
            "opcode": "looks_nextbackdrop",
            "pattern": r"下一个背景"
        },
        "设置大小": {
            "opcode": "looks_setsizeto",
            "pattern": r"将大小设为\s+([\d.]+)",
            "inputs": {"SIZE": 1}
        },
        "大小增加": {
            "opcode": "looks_changesizeby",
            "pattern": r"将大小增加\s+([-\d.]+)",
            "inputs": {"CHANGE": 1}
        },
        "显示": {
            "opcode": "looks_show",
            "pattern": r"^显示$"
        },
        "隐藏": {
            "opcode": "looks_hide",
            "pattern": r"^隐藏$"
        },
        "移至最前": {
            "opcode": "looks_gotofrontback",
            "pattern": r"移至最前层",
            "fields": {"FRONT_BACK": ["front", None]}
        },
        "移至最后": {
            "opcode": "looks_gotofrontback",
            "pattern": r"移至最后层",
            "fields": {"FRONT_BACK": ["back", None]}
        },
        "图层增加": {
            "opcode": "looks_goforwardbackwardlayers",
            "pattern": r"图层增加\s+([\d]+)",
            "fields": {"FORWARD_BACKWARD": ["forward", None]},
            "inputs": {"NUM": 1}
        },
        "图层减少": {
            "opcode": "looks_goforwardbackwardlayers",
            "pattern": r"图层减少\s+([\d]+)",
            "fields": {"FORWARD_BACKWARD": ["backward", None]},
            "inputs": {"NUM": 1}
        },
        "颜色特效增加": {
            "opcode": "looks_changeeffectby",
            "pattern": r"将\s*颜色\s*特效增加\s+([-\d.]+)",
            "fields": {"EFFECT": ["COLOR", None]},
            "inputs": {"CHANGE": 1}
        },
        "颜色特效设为": {
            "opcode": "looks_seteffectto",
            "pattern": r"将\s*颜色\s*特效设为\s+([-\d.]+)",
            "fields": {"EFFECT": ["COLOR", None]},
            "inputs": {"VALUE": 1}
        },
        "清除图形特效": {
            "opcode": "looks_cleargraphiceffects",
            "pattern": r"清除图形特效"
        },
    }
    
    # ==================== 声音积木 ====================
    SOUND = {
        "播放声音": {
            "opcode": "sound_play",
            "pattern": r"播放声音\s+(.+?)(?:\s|$)",
            "inputs": {"SOUND_MENU": 1}
        },
        "播放声音并等待": {
            "opcode": "sound_playuntildone",
            "pattern": r"播放声音\s+(.+?)\s*并等待",
            "inputs": {"SOUND_MENU": 1}
        },
        "停止所有声音": {
            "opcode": "sound_stopallsounds",
            "pattern": r"停止所有声音"
        },
        "音量设为": {
            "opcode": "sound_setvolumeto",
            "pattern": r"将音量设为\s+([\d.]+)",
            "inputs": {"VOLUME": 1}
        },
        "音量增加": {
            "opcode": "sound_changevolumeby",
            "pattern": r"将音量增加\s+([-\d.]+)",
            "inputs": {"VOLUME": 1}
        },
        "音调设为": {
            "opcode": "sound_seteffectto",
            "pattern": r"将音调设为\s+([-\d.]+)",
            "fields": {"EFFECT": ["PITCH", None]},
            "inputs": {"VALUE": 1}
        },
        "清除声音特效": {
            "opcode": "sound_cleareffects",
            "pattern": r"清除声音特效"
        },
    }
    
    # ==================== 控制积木 ====================
    CONTROL = {
        "等待": {
            "opcode": "control_wait",
            "pattern": r"等待\s+(.+)\s*秒",  # 🔥
            "inputs": {"DURATION": 1}
        },
        "重复": {
            "opcode": "control_repeat",
            "pattern": r"重复\s+(.+)\s*次",  # 🔥
            "inputs": {"TIMES": 1},
            "has_substack": True
        },
        "重复执行": {
            "opcode": "control_forever",
            "pattern": r"重复执行|forever",
            "has_substack": True
        },
        "如果": {
            "opcode": "control_if",
            "pattern": r"如果\s+(.+?)\s+那么",
            "inputs": {"CONDITION": 1},
            "has_substack": True
        },
        "等待直到": {
            "opcode": "control_wait_until",
            "pattern": r"等待直到\s+(.+)",
            "inputs": {"CONDITION": 1}
        },
        "重复执行直到": {
            "opcode": "control_repeat_until",
            "pattern": r"重复执行直到\s+(.+)",
            "inputs": {"CONDITION": 1},
            "has_substack": True
        },
        "停止全部": {
            "opcode": "control_stop",
            "pattern": r"停止\s*全部",
            "fields": {"STOP_OPTION": ["all", None]}
        },
        "停止此脚本": {
            "opcode": "control_stop",
            "pattern": r"停止\s*(?:此|这个)脚本",
            "fields": {"STOP_OPTION": ["this script", None]}
        },
        "停止其他脚本": {
            "opcode": "control_stop",
            "pattern": r"停止\s*(?:此|这个)角色的其他脚本",
            "fields": {"STOP_OPTION": ["other scripts in sprite", None]}
        },
        "克隆": {
            "opcode": "control_create_clone_of",
            "pattern": r"克隆\s+(.+)",
            "inputs": {"CLONE_OPTION": 1}
        },
        "当作为克隆体启动": {
            "opcode": "control_start_as_clone",
            "pattern": r"当作为克隆体启动"
        },
        "删除克隆体": {
            "opcode": "control_delete_this_clone",
            "pattern": r"删除此克隆体"
        },
        "广播": {
            "opcode": "event_broadcast",
            "pattern": r"广播\s+(.+?)(?:\s|$)",
            "inputs": {"BROADCAST_INPUT": 1}
        },
        "广播并等待": {
            "opcode": "event_broadcastandwait",
            "pattern": r"广播\s+(.+?)\s*并等待",
            "inputs": {"BROADCAST_INPUT": 1}
        },
    }
    
    # ==================== 侦测积木 ====================
    # 🔥 移除了只能在条件中使用的 reporter 积木
    SENSING = {
        "询问并等待": {
            "opcode": "sensing_askandwait",
            "pattern": r"询问\s+(.+?)\s*并等待",
            "inputs": {"QUESTION": 1}
        },
        "角色属性": {
            "opcode": "sensing_of",
            "pattern": r"(.+?)\s*的\s*(x坐标|y坐标|方向|造型编号|造型名称|大小|音量|背景编号|背景名称)",
            "inputs": {"OBJECT": 1},
            "fields": {"PROPERTY": 2}
        },
        "计时器归零": {
            "opcode": "sensing_resettimer",
            "pattern": r"计时器归零"
        },
        "设置拖动模式": {
            "opcode": "sensing_setdragmode",
            "pattern": r"设置拖动模式为\s+(.+)",
            "fields": {"DRAG_MODE": 1}
        },
    }
    
    # ==================== 运算积木 ====================
    # 🔥 移除了运算符积木，它们应该在表达式中处理
    OPERATORS = {
        "四舍五入": {
            "opcode": "operator_round",
            "pattern": r"四舍五入\s+(.+)",
            "inputs": {"NUM": 1}
        },
        "数学运算": {
            "opcode": "operator_mathop",
            "pattern": r"(abs|floor|ceiling|sqrt|sin|cos|tan|asin|acos|atan|ln|log|e\^|10\^)\s+(.+)",
            "fields": {"OPERATOR": 1},
            "inputs": {"NUM": 2}
        },
        "第几个字符": {
            "opcode": "operator_letter_of",
            "pattern": r"第\s+([\d]+)\s*个字符是\s+(.+)",
            "inputs": {"LETTER": 1, "STRING": 2}
        },
        "字符串长度": {
            "opcode": "operator_length",
            "pattern": r"字符串长度\s+(.+)",
            "inputs": {"STRING": 1}
        },
    }
    
    # ==================== 变量积木 ====================
    VARIABLES = {
        "设置变量": {
            "opcode": "data_setvariableto",
            "pattern": r"设置\s+(.+?)\s+为\s+(.+)$",  # 🔥 最后参数到行尾
            "fields": {"VARIABLE": 1},
            "inputs": {"VALUE": 2}
        },
        "变量增加": {
            "opcode": "data_changevariableby",
            "pattern": r"将\s+(.+?)\s+增加\s+(.+)$",  # 🔥
            "fields": {"VARIABLE": 1},
            "inputs": {"VALUE": 2}
        },
        "显示变量": {
            "opcode": "data_showvariable",
            "pattern": r"显示变量\s+(.+?)(?:\s|$)",
            "fields": {"VARIABLE": 1}
        },
        "隐藏变量": {
            "opcode": "data_hidevariable",
            "pattern": r"隐藏变量\s+(.+?)(?:\s|$)",
            "fields": {"VARIABLE": 1}
        },
        "添加到列表": {
            "opcode": "data_addtolist",
            "pattern": r"添加\s+(.+?)\s*到\s+(.+?)(?:\s|$)",
            "inputs": {"ITEM": 1},
            "fields": {"LIST": 2}
        },
        "删除列表项": {
            "opcode": "data_deleteoflist",
            "pattern": r"删除\s+(.+?)\s*的第\s+(.+?)\s*项(?:\s|$)",
            "fields": {"LIST": 1},
            "inputs": {"INDEX": 2}
        },
        "清空列表": {
            "opcode": "data_deletealloflist",
            "pattern": r"清空\s+(.+?)(?:\s|$)",
            "fields": {"LIST": 1}
        },
        "插入列表": {
            "opcode": "data_insertatlist",
            "pattern": r"插入\s+(.+?)\s*到\s+(.+?)\s*的第\s+(.+?)\s*项(?:\s|$)",
            "inputs": {"ITEM": 1, "INDEX": 3},
            "fields": {"LIST": 2}
        },
        "替换列表项": {
            "opcode": "data_replaceitemoflist",
            "pattern": r"替换\s+(.+?)\s*的第\s+(.+?)\s*项为\s+(.+?)(?:\s|$)",
            "fields": {"LIST": 1},
            "inputs": {"INDEX": 2, "ITEM": 3}
        },
    }
    
    # ==================== 画笔积木 ====================
    PEN = {
        "清空": {
            "opcode": "pen_clear",
            "pattern": r"^清空$"
        },
        "图章": {
            "opcode": "pen_stamp",
            "pattern": r"^图章$"
        },
        "落笔": {
            "opcode": "pen_penDown",
            "pattern": r"^落笔$"
        },
        "抬笔": {
            "opcode": "pen_penUp",
            "pattern": r"^抬笔$"
        },
        "笔迹颜色": {
            "opcode": "pen_setPenColorToColor",
            "pattern": r"将笔的颜色设为\s+(#[0-9A-Fa-f]{6})",
            "inputs": {"COLOR": 1}
        },
        "笔迹粗细": {
            "opcode": "pen_setPenSizeTo",
            "pattern": r"将笔的粗细设为\s+([\d.]+)",
            "inputs": {"SIZE": 1}
        },
        "笔迹粗细增加": {
            "opcode": "pen_changePenSizeBy",
            "pattern": r"将笔的粗细增加\s+([-\d.]+)",
            "inputs": {"SIZE": 1}
        },
        "笔迹颜色增加": {
            "opcode": "pen_changePenColorParamBy",
            "pattern": r"将笔的\s*颜色\s*增加\s+([-\d.]+)",
            "fields": {"COLOR_PARAM": ["color", None]},
            "inputs": {"VALUE": 1}
        },
        "笔迹亮度增加": {
            "opcode": "pen_changePenColorParamBy",
            "pattern": r"将笔的\s*亮度\s*增加\s+([-\d.]+)",
            "fields": {"COLOR_PARAM": ["brightness", None]},
            "inputs": {"VALUE": 1}
        },
    }
    
    @classmethod
    def get_all_blocks(cls) -> BlocksDict:
        """获取所有积木定义

        Returns:
            BlocksDict: 包含所有积木定义的字典
        """
        return {
            **cls.EVENTS,
            **cls.MOTION,
            **cls.LOOKS,
            **cls.SOUND,
            **cls.CONTROL,
            **cls.SENSING,
            **cls.OPERATORS,
            **cls.VARIABLES,
            **cls.PEN,
        }