"""
主窗口
"""
import os
import sys
import tempfile
from PyQt5.QtWidgets import (QMainWindow, QAction, QFileDialog, QMessageBox,
                             QTextEdit, QVBoxLayout, QWidget, QSplitter, QApplication,
                             QDialog, QLabel, QLineEdit, QPushButton, QHBoxLayout,
                             QCheckBox, QGridLayout, QMenu, QDockWidget)
from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QFont, QTextCursor, QTextDocument
from .editor import CodeEditor
from .syntax_tree import SyntaxTreePanel
from compiler.parser import ScratchLangParser

class MainWindow(QMainWindow):
    MAX_RECENT_FILES = 5

    def __init__(self):
        super().__init__()
        self.current_file = None
        self.recent_files = []
        self.security_enabled = True
        self.auto_scale_costumes = False
        self.max_costume_size = 480
        self.settings = QSettings("ScratchLang", "IDE")
        self.load_settings()
        self.init_ui()
        self.setup_autosave()
    
    def init_ui(self):
        self.setWindowTitle("ScratchLang IDE")
        self.setGeometry(100, 100, 1200, 800)

        # 创建编辑器
        self.editor = CodeEditor()
        self.editor.setPlaceholderText("在这里输入ScratchLang代码...")

        # 连接语法错误信号
        self.editor.syntax_errors_changed.connect(self.on_syntax_errors_changed)

        # 连接文本变化信号以更新语法树
        self.editor.textChanged.connect(self.update_syntax_tree)

        # 创建输出窗口
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setMaximumHeight(150)
        self.output.setFont(QFont("Consolas", 10))

        # 布局
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.editor)
        splitter.addWidget(self.output)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(splitter)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setCentralWidget(container)

        # 创建语法树面板（侧边栏）
        self.syntax_tree_panel = SyntaxTreePanel()
        self.syntax_tree_dock = QDockWidget("语法树", self)
        self.syntax_tree_dock.setWidget(self.syntax_tree_panel)
        self.syntax_tree_dock.setMinimumWidth(250)
        self.addDockWidget(Qt.RightDockWidgetArea, self.syntax_tree_dock)

        # 创建菜单
        self.create_menus()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建状态栏
        self.statusBar().showMessage("就绪")
        
        # 加载示例代码
        self.load_example()
    
    def create_menus(self):
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        new_action = QAction("新建(&N)", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("打开(&O)", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("保存(&S)", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("另存为(&A)", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        file_menu.addSeparator()

        # 最近打开的文件子菜单
        self.recent_menu = QMenu("最近打开(&R)", self)
        file_menu.addMenu(self.recent_menu)
        self.update_recent_files_menu()

        file_menu.addSeparator()

        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")
        
        undo_action = QAction("撤销(&U)", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("重做(&R)", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("剪切(&T)", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("复制(&C)", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("粘贴(&P)", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_action)

        edit_menu.addSeparator()

        find_action = QAction("查找(&F)", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_action)

        replace_action = QAction("替换(&H)", self)
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(self.show_replace_dialog)
        edit_menu.addAction(replace_action)

        # 插入菜单
        insert_menu = menubar.addMenu("插入(&I)")
        
        sprite_action = QAction("插入角色(&P)", self)
        sprite_action.triggered.connect(self.insert_sprite)
        insert_menu.addAction(sprite_action)
        
        stage_action = QAction("插入舞台(&T)", self)
        stage_action.triggered.connect(self.insert_stage)
        insert_menu.addAction(stage_action)
        
        insert_menu.addSeparator()
        
        costume_action = QAction("插入造型(&C)", self)
        costume_action.triggered.connect(self.insert_costume)
        insert_menu.addAction(costume_action)
        
        backdrop_action = QAction("插入背景(&B)", self)
        backdrop_action.triggered.connect(self.insert_backdrop)
        insert_menu.addAction(backdrop_action)
        
        sound_action = QAction("插入音效(&S)", self)
        sound_action.triggered.connect(self.insert_sound)
        insert_menu.addAction(sound_action)
        
        # 编译菜单
        build_menu = menubar.addMenu("编译(&B)")

        compile_action = QAction("快速编译(&C)", self)
        compile_action.setShortcut("F5")
        compile_action.triggered.connect(self.compile_project)
        build_menu.addAction(compile_action)

        build_menu.addSeparator()

        decompile_action = QAction("反编译 Scratch 项目(&D)", self)
        decompile_action.setShortcut("F6")
        decompile_action.triggered.connect(self.decompile_sb3)
        build_menu.addAction(decompile_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        doc_action = QAction("文档(&D)", self)
        doc_action.setShortcut("F1")
        doc_action.triggered.connect(self.show_documentation)
        help_menu.addAction(doc_action)
        
        examples_action = QAction("示例代码(&E)", self)
        examples_action.triggered.connect(self.load_example)
        help_menu.addAction(examples_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")

        self.dark_theme_action = QAction("深色主题", self)
        self.dark_theme_action.setCheckable(True)
        self.dark_theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.dark_theme_action)

        view_menu.addSeparator()

        self.security_action = QAction("启用路径安全检查", self)
        self.security_action.setCheckable(True)
        self.security_action.triggered.connect(self.toggle_security)
        view_menu.addAction(self.security_action)

        view_menu.addSeparator()

        settings_action = QAction("编译器设置(&S)", self)
        settings_action.triggered.connect(self.show_settings_dialog)
        view_menu.addAction(settings_action)

        # 加载主题设置
        is_dark = self.settings.value("dark_theme", False, type=bool)
        self.dark_theme_action.setChecked(is_dark)
        if is_dark:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

        # 加载安全设置
        self.security_action.setChecked(self.security_enabled)
    
    def create_toolbar(self):
        toolbar = self.addToolBar("工具栏")
        toolbar.setMovable(False)
        
        new_action = QAction("新建", self)
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
        
        open_action = QAction("打开", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction("保存", self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        compile_action = QAction("编译", self)
        compile_action.triggered.connect(self.compile_project)
        toolbar.addAction(compile_action)
        
        toolbar.addSeparator()
        
        costume_action = QAction("造型", self)
        costume_action.triggered.connect(self.insert_costume)
        toolbar.addAction(costume_action)
        
        backdrop_action = QAction("背景", self)
        backdrop_action.triggered.connect(self.insert_backdrop)
        toolbar.addAction(backdrop_action)
        
        sound_action = QAction("音效", self)
        sound_action.triggered.connect(self.insert_sound)
        toolbar.addAction(sound_action)
    
    def get_safe_path(self, filepath):
        """获取安全的路径字符串"""
        filepath = os.path.normpath(filepath).replace('\\', '/')
        
        if os.path.isabs(filepath):
            try:
                if self.current_file:
                    base_dir = os.path.dirname(os.path.abspath(self.current_file))
                else:
                    base_dir = os.getcwd()
                
                file_parts = os.path.splitdrive(filepath)
                base_parts = os.path.splitdrive(base_dir)
                
                if file_parts[0] and base_parts[0]:
                    if file_parts[0].upper() == base_parts[0].upper():
                        rel = os.path.relpath(filepath, base_dir).replace('\\', '/')
                        if not rel.startswith('..') or rel.count('../') <= 2:
                            return rel
            except:
                pass
        
        return filepath
    
    def new_file(self):
        """新建文件"""
        if self.check_save_changes():
            self.editor.clear()
            self.current_file = None
            self.setWindowTitle("ScratchLang IDE - 新文件")
            self.statusBar().showMessage("新建文件")
    
    def open_file(self):
        """打开文件"""
        if not self.check_save_changes():
            return
        
        filename, _ = QFileDialog.getOpenFileName(
            self, "打开文件", "", 
            "ScratchLang Files (*.sl);;All Files (*)"
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.editor.setPlainText(f.read())
                self.current_file = filename
                self.setWindowTitle(f"ScratchLang IDE - {os.path.basename(filename)}")
                self.statusBar().showMessage(f"已打开: {filename}")
                self.add_to_recent_files(filename)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法打开文件:\n{e}")
    
    def save_file(self):
        """保存文件"""
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
                self.statusBar().showMessage(f"已保存: {self.current_file}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败:\n{e}")
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """另存为"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "另存为", "", 
            "ScratchLang Files (*.sl);;All Files (*)"
        )
        if filename:
            if not filename.endswith('.sl'):
                filename += '.sl'
            self.current_file = filename
            self.save_file()
    
    def check_save_changes(self):
        """检查是否需要保存更改"""
        if self.editor.document().isModified():
            reply = QMessageBox.question(
                self, "保存更改",
                "文档已修改，是否保存？",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                self.save_file()
                return True
            elif reply == QMessageBox.Cancel:
                return False
        return True
    
    def compile_project(self):
        """编译项目"""
        self.output.clear()
        self.output.append("🔨 准备编译...")
        QApplication.processEvents()
        
        # 询问保存方式
        reply = QMessageBox.question(
            self,
            "选择保存方式",
            "请选择编译输出方式：\n\n"
            "• Yes - 快速保存到 output.sb3（推荐）\n"
            "• No - 选择保存位置和文件名\n"
            "• Cancel - 取消编译",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Cancel:
            self.output.append("⚠️ 编译已取消")
            self.statusBar().showMessage("已取消")
            return
        
        temp_file = None
        try:
            # 保存临时文件
            fd, temp_file = tempfile.mkstemp(suffix='.sl', prefix='scratch_compile_')
            os.close(fd)
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            
            # 解析代码
            self.output.append("🔍 解析代码...")
            QApplication.processEvents()

            parser = ScratchLangParser(
                security_enabled=self.security_enabled,
                auto_scale_costumes=self.auto_scale_costumes,
                max_costume_size=self.max_costume_size
            )
            parser.parse_file(temp_file)
            
            self.output.append("✅ 解析完成")
            QApplication.processEvents()
            
            # 确定保存路径
            if reply == QMessageBox.Yes:
                # 快速保存
                output_file = "output.sb3"
                self.output.append(f"💾 快速保存模式")
            else:
                # 选择路径保存
                self.output.append("📂 请在对话框中选择保存位置...")
                QApplication.processEvents()
                
                output_file, _ = QFileDialog.getSaveFileName(
                    self,
                    "保存SB3文件",
                    "",
                    "Scratch 3.0 (*.sb3)"
                )
                
                if not output_file:
                    self.output.append("⚠️ 用户取消保存")
                    self.statusBar().showMessage("已取消")
                    return
                
                if not output_file.endswith('.sb3'):
                    output_file += '.sb3'
            
            # 编译
            self.output.append(f"📦 生成文件: {os.path.basename(output_file)}")
            QApplication.processEvents()
            
            parser.compile(output_file)
            
            # 显示成功信息
            self.output.append("")
            self.output.append("="*50)
            self.output.append("✅ 编译成功!")
            self.output.append(f"📁 文件位置: {os.path.abspath(output_file)}")
            self.output.append("="*50)
            
            for target in parser.builder.project['targets']:
                if target['isStage']:
                    self.output.append(f"🎭 舞台: {len(target['costumes'])} 个背景, {len(target['blocks'])} 个积木")
                else:
                    self.output.append(f"🐱 {target['name']}: {len(target['costumes'])} 个造型, {len(target['blocks'])} 个积木")
            
            QApplication.processEvents()
            self.statusBar().showMessage("编译成功！", 5000)
            
            # 询问是否打开文件夹
            open_reply = QMessageBox.question(
                self, "编译成功",
                f"✅ 编译完成！\n\n"
                f"文件已保存到:\n{os.path.abspath(output_file)}\n\n"
                f"是否打开文件所在文件夹？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if open_reply == QMessageBox.Yes:
                import subprocess
                folder = os.path.dirname(os.path.abspath(output_file)) or '.'
                if os.name == 'nt':
                    subprocess.Popen(f'explorer /select,"{os.path.abspath(output_file)}"')
                else:
                    subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', folder])
        
        except Exception as e:
            self.output.append(f"\n❌ 错误: {str(e)}")
            QMessageBox.critical(self, "错误", f"编译失败:\n{str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)

    def decompile_sb3(self):
        """反编译 Scratch 项目"""
        self.output.clear()
        self.output.append("🔄 准备反编译...")
        QApplication.processEvents()

        # 选择 sb3 文件
        sb3_file, _ = QFileDialog.getOpenFileName(
            self, "选择 Scratch 项目", "",
            "Scratch 3.0 (*.sb3);;All Files (*)"
        )

        if not sb3_file:
            self.output.append("⚠️ 用户取消")
            return

        try:
            from compiler.decompiler import SB3Decompiler

            self.output.append(f"📂 读取文件: {os.path.basename(sb3_file)}")
            QApplication.processEvents()

            decompiler = SB3Decompiler()
            sl_code = decompiler.decompile(sb3_file)

            # 将代码显示在编辑器中
            self.editor.setPlainText(sl_code)

            self.output.append("")
            self.output.append("="*50)
            self.output.append("✅ 反编译成功!")
            self.output.append(f"📁 源文件: {os.path.basename(sb3_file)}")
            self.output.append("="*50)

            self.statusBar().showMessage("反编译成功！", 5000)

        except Exception as e:
            self.output.append(f"\n❌ 错误: {str(e)}")
            QMessageBox.critical(self, "错误", f"反编译失败:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def show_settings_dialog(self):
        """显示设置对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("编译器设置")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout()

        # 图片缩放设置
        scale_group = QWidget()
        scale_layout = QVBoxLayout()

        self.scale_checkbox = QCheckBox("启用造型自动缩放")
        self.scale_checkbox.setChecked(self.auto_scale_costumes)
        scale_layout.addWidget(self.scale_checkbox)

        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("最大尺寸:"))
        self.size_input = QLineEdit(str(self.max_costume_size))
        self.size_input.setMaximumWidth(100)
        size_layout.addWidget(self.size_input)
        size_layout.addWidget(QLabel("像素"))
        size_layout.addStretch()
        scale_layout.addLayout(size_layout)

        scale_group.setLayout(scale_layout)
        layout.addWidget(scale_group)

        # 按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(lambda: self.save_settings(dialog))
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.exec_()

    def save_settings(self, dialog):
        """保存设置"""
        self.auto_scale_costumes = self.scale_checkbox.isChecked()
        try:
            self.max_costume_size = int(self.size_input.text())
        except ValueError:
            QMessageBox.warning(self, "警告", "最大尺寸必须是数字")
            return

        self.settings.setValue("auto_scale_costumes", self.auto_scale_costumes)
        self.settings.setValue("max_costume_size", self.max_costume_size)

        dialog.accept()
        QMessageBox.information(self, "设置", "设置已保存！")

    def insert_costume(self):
        """插入造型"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", 
            "图片文件 (*.png *.jpg *.jpeg *.svg);;All Files (*)"
        )
        if filename:
            safe_path = self.get_safe_path(filename)
            self.editor.insertPlainText(f"造型: {safe_path}\n")
            self.statusBar().showMessage(f"已插入造型: {os.path.basename(filename)}")
    
    def insert_backdrop(self):
        """插入背景"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "选择背景图片", "", 
            "图片文件 (*.png *.jpg *.jpeg *.svg);;All Files (*)"
        )
        if filename:
            safe_path = self.get_safe_path(filename)
            self.editor.insertPlainText(f"背景: {safe_path}\n")
            self.statusBar().showMessage(f"已插入背景: {os.path.basename(filename)}")
    
    def insert_sound(self):
        """插入音效"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "选择音效", "", 
            "音频文件 (*.mp3 *.wav);;All Files (*)"
        )
        if filename:
            safe_path = self.get_safe_path(filename)
            self.editor.insertPlainText(f"音效: {safe_path}\n")
            self.statusBar().showMessage(f"已插入音效: {os.path.basename(filename)}")
    
    def insert_sprite(self):
        """插入角色模板"""
        template = """
# 新角色
当绿旗被点击
  说 "你好！" 2秒
  移动 10 步
"""
        self.editor.insertPlainText(template)
        self.statusBar().showMessage("已插入角色模板")
    
    def insert_stage(self):
        """插入舞台模板"""
        template = """
@ 舞台
背景: images/bg1.png

当绿旗被点击
  切换背景到 bg1
"""
        self.editor.insertPlainText(template)
        self.statusBar().showMessage("已插入舞台模板")
    
    def load_example(self):
        """加载示例代码"""
        example = """: 开始

@ 舞台
当绿旗被点击
  切换背景到 backdrop1

# 小猫
当绿旗被点击
  说 "欢迎使用 ScratchLang！" 2秒
  移到 0 0
  
  重复 4 次
    移动 100 步
    旋转右 90 度
    等待 0.5 秒
  结束
  
  说 "完成了一个正方形！" 2秒

# 小狗
当绿旗被点击
  重复执行
    移动 5 步
    碰到边缘就反弹
  结束
"""
        self.editor.setPlainText(example)
        self.statusBar().showMessage("已加载示例代码")
    
    def show_documentation(self):
        """显示文档"""
        doc_text = """ScratchLang 快速参考

【基本结构】
: 开始                  # 项目开始
@ 舞台                  # 切换到舞台
# 角色名                # 创建角色

【舞台】
@ 舞台
背景: path/to/bg.png    # 添加背景
切换背景到 bg1          # 切换背景
当背景换成 bg1          # 背景切换事件

【事件】
当绿旗被点击
当按下 空格键 键
当收到 消息名

【动作】
移动 10 步
旋转右 90 度
移到 0 0
碰到边缘就反弹

【外观】
说 "文本" 2秒
显示 / 隐藏

【控制】
等待 1 秒
重复 10 次
  ...
结束
重复执行
  ...
结束

更多详情请查看 README.md
"""
        QMessageBox.information(self, "文档", doc_text)
    
    def show_about(self):
        """显示关于"""
        about_text = """ScratchLang IDE v1.0

将文本代码编译成 Scratch 3.0 项目

特性:
• 简洁的文本语法
• 完整支持 Scratch 积木
• 图片和音效导入
• 舞台背景管理
• 语法高亮
• 一键编译

符号说明:
: 开始      - 项目开始
@ 舞台      - 切换到舞台
# 角色名    - 创建/切换角色

Copyright © 2024
开源协议: MIT License
"""
        QMessageBox.about(self, "关于", about_text)

    def on_syntax_errors_changed(self, errors):
        """处理语法错误变化"""
        if not errors:
            self.output.clear()
            self.output.setStyleSheet("")
            self.statusBar().showMessage("语法检查通过", 2000)
            return

        self.output.clear()
        self.output.append("⚠️ 语法检查发现以下问题：\n")
        for line_num, message in errors:
            self.output.append(f"  第 {line_num} 行: {message}")
        self.output.append(f"\n共 {len(errors)} 个问题")
        self.statusBar().showMessage(f"发现 {len(errors)} 个语法问题")

    def update_syntax_tree(self):
        """更新语法树面板"""
        code = self.editor.toPlainText()
        self.syntax_tree_panel.update_tree(code)

    def closeEvent(self, event):
        """关闭窗口事件"""
        if self.check_save_changes():
            self.save_settings()
            event.accept()
        else:
            event.ignore()

    # ==================== 设置和自动保存 ====================

    def load_settings(self):
        """加载设置"""
        self.recent_files = self.settings.value("recent_files", []) or []
        self.security_enabled = self.settings.value("security_enabled", True, type=bool)
        self.auto_scale_costumes = self.settings.value("auto_scale_costumes", False, type=bool)
        self.max_costume_size = self.settings.value("max_costume_size", 480, type=int)

    def save_settings(self):
        """保存设置"""
        self.settings.setValue("recent_files", self.recent_files)
        self.settings.setValue("security_enabled", self.security_enabled)

    def setup_autosave(self):
        """设置自动保存定时器"""
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(60000)  # 每60秒自动保存

    def autosave(self):
        """自动保存"""
        if self.current_file and self.editor.document().isModified():
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
                self.editor.document().setModified(False)
                self.statusBar().showMessage("自动保存完成", 2000)
            except Exception:
                pass  # 静默失败

    def add_to_recent_files(self, filepath):
        """添加到最近打开的文件列表"""
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
        self.recent_files.insert(0, filepath)
        self.recent_files = self.recent_files[:self.MAX_RECENT_FILES]
        self.update_recent_files_menu()

    def update_recent_files_menu(self):
        """更新最近打开的文件菜单"""
        self.recent_menu.clear()
        if not self.recent_files:
            action = QAction("(无)", self)
            action.setEnabled(False)
            self.recent_menu.addAction(action)
        else:
            for filepath in self.recent_files:
                action = QAction(os.path.basename(filepath), self)
                action.setData(filepath)
                action.triggered.connect(self.open_recent_file)
                self.recent_menu.addAction(action)

            self.recent_menu.addSeparator()
            clear_action = QAction("清除列表", self)
            clear_action.triggered.connect(self.clear_recent_files)
            self.recent_menu.addAction(clear_action)

    def open_recent_file(self):
        """打开最近的文件"""
        action = self.sender()
        if action:
            filepath = action.data()
            if os.path.exists(filepath):
                if self.check_save_changes():
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            self.editor.setPlainText(f.read())
                        self.current_file = filepath
                        self.setWindowTitle(f"ScratchLang IDE - {os.path.basename(filepath)}")
                        self.statusBar().showMessage(f"已打开: {filepath}")
                        self.add_to_recent_files(filepath)
                    except Exception as e:
                        QMessageBox.critical(self, "错误", f"无法打开文件:\n{e}")
            else:
                QMessageBox.warning(self, "警告", f"文件不存在:\n{filepath}")
                self.recent_files.remove(filepath)
                self.update_recent_files_menu()

    def clear_recent_files(self):
        """清除最近打开的文件列表"""
        self.recent_files = []
        self.update_recent_files_menu()

    # ==================== 主题切换 ====================

    def toggle_theme(self):
        """切换主题"""
        if self.dark_theme_action.isChecked():
            self.apply_dark_theme()
            self.settings.setValue("dark_theme", True)
        else:
            self.apply_light_theme()
            self.settings.setValue("dark_theme", False)

    def apply_dark_theme(self):
        """应用深色主题"""
        dark_style = """
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QPlainTextEdit, QTextEdit {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                selection-background-color: #264f78;
            }
            QMenuBar {
                background-color: #2d2d2d;
                color: #d4d4d4;
            }
            QMenuBar::item:selected {
                background-color: #3c3c3c;
            }
            QMenu {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
            QToolBar {
                background-color: #2d2d2d;
                border: none;
            }
            QStatusBar {
                background-color: #007acc;
                color: white;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                padding: 3px;
            }
            QCheckBox {
                color: #d4d4d4;
            }
            QLabel {
                color: #d4d4d4;
            }
            QSplitter::handle {
                background-color: #3c3c3c;
            }
        """
        self.setStyleSheet(dark_style)
        self.statusBar().showMessage("已切换到深色主题", 2000)

    def apply_light_theme(self):
        """应用浅色主题"""
        self.setStyleSheet("")  # 恢复默认样式
        self.statusBar().showMessage("已切换到浅色主题", 2000)

    def toggle_security(self):
        """切换安全检查"""
        self.security_enabled = self.security_action.isChecked()
        self.settings.setValue("security_enabled", self.security_enabled)
        status = "已启用" if self.security_enabled else "已禁用"
        self.statusBar().showMessage(f"路径安全检查{status}", 2000)

    def show_find_dialog(self):
        """显示查找对话框"""
        dialog = FindReplaceDialog(self, replace_mode=False)
        dialog.show()

    def show_replace_dialog(self):
        """显示替换对话框"""
        dialog = FindReplaceDialog(self, replace_mode=True)
        dialog.show()

    def find_text(self, text, case_sensitive=False, whole_word=False):
        """查找文本"""
        if not text:
            return False

        flags = QTextDocument.FindFlags()
        if case_sensitive:
            flags |= QTextDocument.FindCaseSensitively
        if whole_word:
            flags |= QTextDocument.FindWholeWords

        cursor = self.editor.textCursor()
        found = self.editor.find(text, flags)

        if not found:
            # 从头开始搜索
            cursor.movePosition(QTextCursor.Start)
            self.editor.setTextCursor(cursor)
            found = self.editor.find(text, flags)

        if found:
            self.statusBar().showMessage(f"找到: {text}")
        else:
            self.statusBar().showMessage(f"未找到: {text}")

        return found

    def replace_text(self, find_text, replace_text, case_sensitive=False, whole_word=False):
        """替换当前选中的文本"""
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            if case_sensitive:
                match = selected == find_text
            else:
                match = selected.lower() == find_text.lower()

            if match:
                cursor.insertText(replace_text)
                self.statusBar().showMessage("已替换")
                return True

        # 查找下一个
        return self.find_text(find_text, case_sensitive, whole_word)

    def replace_all_text(self, find_text, replace_text, case_sensitive=False, whole_word=False):
        """替换所有匹配的文本"""
        if not find_text:
            return 0

        content = self.editor.toPlainText()
        if case_sensitive:
            if whole_word:
                import re
                pattern = r'\b' + re.escape(find_text) + r'\b'
                new_content, count = re.subn(pattern, replace_text, content)
            else:
                count = content.count(find_text)
                new_content = content.replace(find_text, replace_text)
        else:
            if whole_word:
                import re
                pattern = r'\b' + re.escape(find_text) + r'\b'
                new_content, count = re.subn(pattern, replace_text, content, flags=re.IGNORECASE)
            else:
                import re
                pattern = re.escape(find_text)
                new_content, count = re.subn(pattern, replace_text, content, flags=re.IGNORECASE)

        if count > 0:
            self.editor.setPlainText(new_content)
            self.statusBar().showMessage(f"已替换 {count} 处")

        return count


class FindReplaceDialog(QDialog):
    """查找/替换对话框"""

    def __init__(self, parent, replace_mode=False):
        super().__init__(parent)
        self.parent_window = parent
        self.replace_mode = replace_mode
        self.init_ui()

    def init_ui(self):
        if self.replace_mode:
            self.setWindowTitle("替换")
        else:
            self.setWindowTitle("查找")

        self.setFixedSize(400, 180 if self.replace_mode else 120)

        layout = QGridLayout(self)

        # 查找输入框
        layout.addWidget(QLabel("查找:"), 0, 0)
        self.find_input = QLineEdit()
        layout.addWidget(self.find_input, 0, 1, 1, 2)

        # 替换输入框（仅替换模式）
        if self.replace_mode:
            layout.addWidget(QLabel("替换为:"), 1, 0)
            self.replace_input = QLineEdit()
            layout.addWidget(self.replace_input, 1, 1, 1, 2)

        # 选项
        options_layout = QHBoxLayout()
        self.case_checkbox = QCheckBox("区分大小写")
        self.word_checkbox = QCheckBox("全字匹配")
        options_layout.addWidget(self.case_checkbox)
        options_layout.addWidget(self.word_checkbox)
        row = 2 if self.replace_mode else 1
        layout.addLayout(options_layout, row, 0, 1, 3)

        # 按钮
        btn_layout = QHBoxLayout()
        find_btn = QPushButton("查找下一个")
        find_btn.clicked.connect(self.find_next)
        btn_layout.addWidget(find_btn)

        if self.replace_mode:
            replace_btn = QPushButton("替换")
            replace_btn.clicked.connect(self.replace)
            btn_layout.addWidget(replace_btn)

            replace_all_btn = QPushButton("全部替换")
            replace_all_btn.clicked.connect(self.replace_all)
            btn_layout.addWidget(replace_all_btn)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)

        row = 3 if self.replace_mode else 2
        layout.addLayout(btn_layout, row, 0, 1, 3)

    def find_next(self):
        text = self.find_input.text()
        self.parent_window.find_text(
            text,
            self.case_checkbox.isChecked(),
            self.word_checkbox.isChecked()
        )

    def replace(self):
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        self.parent_window.replace_text(
            find_text,
            replace_text,
            self.case_checkbox.isChecked(),
            self.word_checkbox.isChecked()
        )

    def replace_all(self):
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        count = self.parent_window.replace_all_text(
            find_text,
            replace_text,
            self.case_checkbox.isChecked(),
            self.word_checkbox.isChecked()
        )
        if count == 0:
            QMessageBox.information(self, "替换", "未找到匹配项")