"""
积木参考面板 - 显示所有可用的积木块
"""
from PyQt5.QtWidgets import (QTreeWidget, QTreeWidgetItem, QVBoxLayout,
                             QWidget, QTextEdit, QSplitter)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class SyntaxTreePanel(QWidget):
    """积木参考面板"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.populate_blocks()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Vertical)

        # 积木树
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("可用积木")
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        splitter.addWidget(self.tree)

        # 用法说明
        self.usage_text = QTextEdit()
        self.usage_text.setReadOnly(True)
        self.usage_text.setMaximumHeight(150)
        self.usage_text.setPlaceholderText("双击积木查看参数说明和用法")
        splitter.addWidget(self.usage_text)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

    def add_block(self, parent, block_text, usage):
        """添加积木项"""
        item = QTreeWidgetItem(parent, [block_text])
        item.setData(0, Qt.UserRole, usage)

    def populate_blocks(self):
        """填充所有可用的积木块"""
        self.tree.clear()

        # 事件积木
        events = QTreeWidgetItem(self.tree, ["[事件]"])
        self.add_block(events, "当绿旗被点击", "触发：点击绿旗\n用法：当绿旗被点击")
        self.add_block(events, "当按下 [键] 键", "参数：键名（空格/上/下/左/右/a-z）\n用法：当按下 空格 键")
        self.add_block(events, "当角色被点击", "触发：点击角色\n用法：当角色被点击")
        self.add_block(events, "当舞台被点击", "触发：点击舞台\n用法：当舞台被点击")
        self.add_block(events, "当收到 [消息]", "参数：消息名\n用法：当收到 开始")
        self.add_block(events, "当背景换成 [背景]", "参数：背景名\n用法：当背景换成 背景1")
        self.add_block(events, "当作为克隆体启动", "触发：克隆体启动\n用法：当作为克隆体启动")

        # 动作积木
        motion = QTreeWidgetItem(self.tree, ["[动作]"])
        self.add_block(motion, "移动 [步数] 步", "参数：步数（数字）\n用法：移动 10 步")
        self.add_block(motion, "旋转右 [角度] 度", "参数：角度（数字）\n用法：旋转右 90 度")
        self.add_block(motion, "旋转左 [角度] 度", "参数：角度（数字）\n用法：旋转左 90 度")
        self.add_block(motion, "移到 [x] [y]", "参数：x坐标, y坐标\n用法：移到 100 200")
        self.add_block(motion, "移到 [目标]", "参数：目标（鼠标指针/角色名）\n用法：移到 鼠标指针")
        self.add_block(motion, "面向 [方向] 方向", "参数：方向（0-360）\n用法：面向 90 方向")
        self.add_block(motion, "面向 [目标]", "参数：目标（鼠标指针/角色名）\n用法：面向 鼠标指针")
        self.add_block(motion, "在 [秒] 秒内滑行到 [x] [y]", "参数：秒数, x坐标, y坐标\n用法：在 1 秒内滑行到 100 200")
        self.add_block(motion, "在 [秒] 秒内滑行到 [目标]", "参数：秒数, 目标\n用法：在 1 秒内滑行到 鼠标指针")
        self.add_block(motion, "将x坐标增加 [值]", "参数：增加值\n用法：将x坐标增加 10")
        self.add_block(motion, "将x坐标设为 [值]", "参数：x坐标\n用法：将x坐标设为 100")
        self.add_block(motion, "将y坐标增加 [值]", "参数：增加值\n用法：将y坐标增加 10")
        self.add_block(motion, "将y坐标设为 [值]", "参数：y坐标\n用法：将y坐标设为 100")
        self.add_block(motion, "碰到边缘就反弹", "用法：碰到边缘就反弹")
        self.add_block(motion, "将旋转方式设为 [方式]", "参数：方式（左右翻转/不旋转/任意旋转）\n用法：将旋转方式设为 左右翻转")

        # 外观积木
        looks = QTreeWidgetItem(self.tree, ["[外观]"])
        self.add_block(looks, "说 [内容] [秒] 秒", "参数：内容, 秒数\n用法：说 \"你好\" 2 秒")
        self.add_block(looks, "说 [内容]", "参数：内容\n用法：说 \"你好\"")
        self.add_block(looks, "想 [内容] [秒] 秒", "参数：内容, 秒数\n用法：想 \"嗯...\" 2 秒")
        self.add_block(looks, "想 [内容]", "参数：内容\n用法：想 \"嗯...\"")
        self.add_block(looks, "切换造型到 [造型]", "参数：造型名或编号\n用法：切换造型到 造型1")
        self.add_block(looks, "下一个造型", "用法：下一个造型")
        self.add_block(looks, "切换背景到 [背景]", "参数：背景名或编号\n用法：切换背景到 背景1")
        self.add_block(looks, "下一个背景", "用法：下一个背景")
        self.add_block(looks, "将大小设为 [百分比]", "参数：百分比\n用法：将大小设为 100")
        self.add_block(looks, "将大小增加 [值]", "参数：增加值\n用法：将大小增加 10")
        self.add_block(looks, "显示", "用法：显示")
        self.add_block(looks, "隐藏", "用法：隐藏")
        self.add_block(looks, "移至最前层", "用法：移至最前层")
        self.add_block(looks, "移至最后层", "用法：移至最后层")
        self.add_block(looks, "图层增加 [值]", "参数：增加值\n用法：图层增加 1")
        self.add_block(looks, "图层减少 [值]", "参数：减少值\n用法：图层减少 1")
        self.add_block(looks, "将颜色特效增加 [值]", "参数：增加值\n用法：将颜色特效增加 25")
        self.add_block(looks, "将颜色特效设为 [值]", "参数：值\n用法：将颜色特效设为 50")
        self.add_block(looks, "清除图形特效", "用法：清除图形特效")

        # 声音积木
        sound = QTreeWidgetItem(self.tree, ["[声音]"])
        self.add_block(sound, "播放声音 [声音]", "参数：声音名\n用法：播放声音 喵")
        self.add_block(sound, "播放声音 [声音] 并等待", "参数：声音名\n用法：播放声音 喵 并等待")
        self.add_block(sound, "停止所有声音", "用法：停止所有声音")
        self.add_block(sound, "将音量设为 [值]", "参数：音量(0-100)\n用法：将音量设为 50")
        self.add_block(sound, "将音量增加 [值]", "参数：增加值\n用法：将音量增加 10")
        self.add_block(sound, "将音调设为 [值]", "参数：音调值\n用法：将音调设为 100")
        self.add_block(sound, "清除声音特效", "用法：清除声音特效")

        # 控制积木
        control = QTreeWidgetItem(self.tree, ["[控制]"])
        self.add_block(control, "等待 [秒] 秒", "参数：秒数\n用法：等待 1 秒")
        self.add_block(control, "重复 [次数] 次", "参数：次数\n用法：重复 10 次\n  ...\n结束")
        self.add_block(control, "重复执行", "用法：重复执行\n  ...\n结束")
        self.add_block(control, "如果 [条件] 那么", "参数：条件\n用法：如果 1 > 0 那么\n  ...\n结束")
        self.add_block(control, "等待直到 [条件]", "参数：条件\n用法：等待直到 ~分数 > 100")
        self.add_block(control, "重复执行直到 [条件]", "参数：条件\n用法：重复执行直到 ~分数 > 100\n  ...\n结束")
        self.add_block(control, "停止全部", "用法：停止全部")
        self.add_block(control, "停止此脚本", "用法：停止此脚本")
        self.add_block(control, "停止此角色的其他脚本", "用法：停止此角色的其他脚本")
        self.add_block(control, "克隆 [目标]", "参数：目标（自己/角色名）\n用法：克隆 自己")
        self.add_block(control, "删除此克隆体", "用法：删除此克隆体")
        self.add_block(control, "广播 [消息]", "参数：消息名\n用法：广播 开始")
        self.add_block(control, "广播 [消息] 并等待", "参数：消息名\n用法：广播 开始 并等待")

        # 侦测积木
        sensing = QTreeWidgetItem(self.tree, ["[侦测]"])
        self.add_block(sensing, "询问 [内容] 并等待", "参数：询问内容\n用法：询问 \"你叫什么名字？\" 并等待")
        self.add_block(sensing, "[角色] 的 [属性]", "参数：角色名, 属性\n用法：小猫 的 x坐标")
        self.add_block(sensing, "计时器归零", "用法：计时器归零")
        self.add_block(sensing, "设置拖动模式为 [模式]", "参数：模式（可拖动/不可拖动）\n用法：设置拖动模式为 可拖动")

        # 运算积木
        operators = QTreeWidgetItem(self.tree, ["[运算]"])
        self.add_block(operators, "四舍五入 [数字]", "参数：数字\n用法：四舍五入 3.7")
        self.add_block(operators, "[运算] [数字]", "参数：运算(abs/floor/ceiling/sqrt/sin/cos/tan等), 数字\n用法：abs -5")
        self.add_block(operators, "第 [位置] 个字符是 [字符串]", "参数：位置, 字符串\n用法：第 1 个字符是 \"hello\"")
        self.add_block(operators, "字符串长度 [字符串]", "参数：字符串\n用法：字符串长度 \"hello\"")

        # 变量积木
        variables = QTreeWidgetItem(self.tree, ["[变量]"])
        self.add_block(variables, "变量: [名称] = [值]", "参数：变量名, 初始值\n用法：变量: 分数 = 0")
        self.add_block(variables, "将 [变量] 设为 [值]", "参数：变量名, 值\n用法：将 分数 设为 100")
        self.add_block(variables, "将 [变量] 增加 [值]", "参数：变量名, 值\n用法：将 分数 增加 10")
        self.add_block(variables, "显示变量 [变量]", "参数：变量名\n用法：显示变量 分数")
        self.add_block(variables, "隐藏变量 [变量]", "参数：变量名\n用法：隐藏变量 分数")
        self.add_block(variables, "云变量: [名称] = [值]", "参数：云变量名, 初始值\n用法：云变量: 排名 = 0")

        # 列表积木
        lists = QTreeWidgetItem(self.tree, ["[列表]"])
        self.add_block(lists, "列表: [名称]", "参数：列表名\n用法：列表: 物品")
        self.add_block(lists, "添加 [值] 到 [列表]", "参数：值, 列表名\n用法：添加 \"苹果\" 到 物品")
        self.add_block(lists, "删除 [列表] 的第 [位置] 项", "参数：列表名, 位置\n用法：删除 物品 的第 1 项")
        self.add_block(lists, "清空 [列表]", "参数：列表名\n用法：清空 物品")
        self.add_block(lists, "插入 [值] 到 [列表] 的第 [位置] 项", "参数：值, 列表名, 位置\n用法：插入 \"香蕉\" 到 物品 的第 1 项")
        self.add_block(lists, "替换 [列表] 的第 [位置] 项为 [值]", "参数：列表名, 位置, 值\n用法：替换 物品 的第 1 项为 \"橙子\"")

        # 画笔积木
        pen = QTreeWidgetItem(self.tree, ["[画笔]"])
        self.add_block(pen, "清空", "用法：清空")
        self.add_block(pen, "图章", "用法：图章")
        self.add_block(pen, "落笔", "用法：落笔")
        self.add_block(pen, "抬笔", "用法：抬笔")
        self.add_block(pen, "将笔的颜色设为 [颜色]", "参数：颜色(#RRGGBB)\n用法：将笔的颜色设为 #FF0000")
        self.add_block(pen, "将笔的粗细设为 [值]", "参数：粗细值\n用法：将笔的粗细设为 5")
        self.add_block(pen, "将笔的粗细增加 [值]", "参数：增加值\n用法：将笔的粗细增加 1")
        self.add_block(pen, "将笔的颜色增加 [值]", "参数：增加值\n用法：将笔的颜色增加 10")
        self.add_block(pen, "将笔的亮度增加 [值]", "参数：增加值\n用法：将笔的亮度增加 10")

        # 音乐扩展
        music = QTreeWidgetItem(self.tree, ["[音乐]"])
        self.add_block(music, "演奏音符 [音符] [拍数] 拍", "参数：音符(0-127), 拍数\n用法：演奏音符 60 0.5 拍")
        self.add_block(music, "演奏鼓声 [鼓] [拍数] 拍", "参数：鼓(1-18), 拍数\n用法：演奏鼓声 1 0.25 拍")
        self.add_block(music, "休止 [拍数] 拍", "参数：拍数\n用法：休止 1 拍")
        self.add_block(music, "将乐器设为 [乐器]", "参数：乐器编号(1-21)\n用法：将乐器设为 1")
        self.add_block(music, "将节奏设为 [值]", "参数：节奏值(BPM)\n用法：将节奏设为 120")
        self.add_block(music, "将节奏增加 [值]", "参数：增加值\n用法：将节奏增加 20")

        # 自定义积木
        custom = QTreeWidgetItem(self.tree, ["[自定义积木]"])
        self.add_block(custom, "定义 [名称]([参数])", "参数：积木名, 参数列表\n用法：定义 移动并说话(步数, 内容)\n  ...\n结束")
        self.add_block(custom, "定义 [名称]() 不刷新屏幕", "参数：积木名\n用法：定义 快速计算() 不刷新屏幕\n  ...\n结束")

        # 扩展导入
        extensions = QTreeWidgetItem(self.tree, ["[扩展]"])
        self.add_block(extensions, "导入扩展: \"[文件]\"", "参数：JS文件路径\n用法：导入扩展: \"myext.js\"")
        self.add_block(extensions, "#code# ... #end#", "用法：#code#\nconsole.log('test');\n#end#")

        self.tree.expandAll()

    def on_item_double_clicked(self, item, column):
        """双击显示参数说明"""
        usage = item.data(0, Qt.UserRole)
        if usage:
            self.usage_text.setText(usage)

    def update_tree(self, code):
        """更新树（保留兼容性）"""
        pass
