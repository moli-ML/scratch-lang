"""
常量定义 - ScratchLang 编译器常量
"""

# Scratch 特殊目标值
TARGET_MOUSE = "_mouse_"
TARGET_RANDOM = "_random_"
TARGET_EDGE = "_edge_"
TARGET_STAGE = "_stage_"

# 中文到 Scratch 特殊值的映射
SPECIAL_TARGETS = {
    "鼠标指针": TARGET_MOUSE,
    "鼠标": TARGET_MOUSE,
    "随机位置": TARGET_RANDOM,
    "随机": TARGET_RANDOM,
    "边缘": TARGET_EDGE,
    "舞台": TARGET_STAGE,
    "Stage": TARGET_STAGE,
}

# 中文按键到 Scratch 按键名的映射
KEY_MAP = {
    "空格": "space",
    "空格键": "space",
    "上": "up arrow",
    "上箭头": "up arrow",
    "下": "down arrow",
    "下箭头": "down arrow",
    "左": "left arrow",
    "左箭头": "left arrow",
    "右": "right arrow",
    "右箭头": "right arrow",
    "回车": "enter",
    "任意": "any",
}

# 旋转方式
ROTATION_STYLE_LEFT_RIGHT = "left-right"
ROTATION_STYLE_DONT_ROTATE = "don't rotate"
ROTATION_STYLE_ALL_AROUND = "all around"

ROTATION_STYLES = {
    "左右翻转": ROTATION_STYLE_LEFT_RIGHT,
    "不可旋转": ROTATION_STYLE_DONT_ROTATE,
    "任意旋转": ROTATION_STYLE_ALL_AROUND,
}

# 停止选项
STOP_ALL = "all"
STOP_THIS_SCRIPT = "this script"
STOP_OTHER_SCRIPTS = "other scripts in sprite"

STOP_OPTIONS = {
    "全部": STOP_ALL,
    "此脚本": STOP_THIS_SCRIPT,
    "角色的其他脚本": STOP_OTHER_SCRIPTS,
}

# 拖动模式
DRAG_MODE_DRAGGABLE = "draggable"
DRAG_MODE_NOT_DRAGGABLE = "not draggable"

DRAG_MODES = {
    "可拖动": DRAG_MODE_DRAGGABLE,
    "不可拖动": DRAG_MODE_NOT_DRAGGABLE,
}

# 图层操作
LAYER_FRONT = "front"
LAYER_BACK = "back"

# 文件大小限制（字节）
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_SOUND_SIZE = 20 * 1024 * 1024  # 20MB

# 支持的文件格式
SUPPORTED_IMAGE_FORMATS = {'.png', '.jpg', '.jpeg', '.svg', '.gif', '.bmp'}
SUPPORTED_SOUND_FORMATS = {'.mp3', '.wav', '.ogg'}

# 默认值
DEFAULT_SPRITE_X = 0
DEFAULT_SPRITE_Y = 0
DEFAULT_SPRITE_SIZE = 100
DEFAULT_SPRITE_DIRECTION = 90
DEFAULT_SPRITE_VISIBLE = True

# 舞台尺寸
STAGE_WIDTH = 480
STAGE_HEIGHT = 360
