# ScratchLang - 为键盘侠打造的 Scratch!

<p align="center">
  <img src="https://img.shields.io/badge/版本-v1.3-blue.svg" alt="版本">
  <img src="https://img.shields.io/badge/Python-3.7+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/许可证-MIT-orange.svg" alt="许可证">
  <img src="https://img.shields.io/badge/完成度-95%25-brightgreen.svg" alt="完成度">
</p>

---

> 厌倦了在屏幕上拖拽积木？
> 想用键盘敲出闪电般的速度，创造出酷炫的 Scratch 动画和游戏吗？
> **ScratchLang** 就是你的答案！它让你像写诗一样编写 Scratch 代码，然后一键变身为标准的 `.sb3` 项目文件！

## 核心特性

*   **文本化编程**：告别鼠标，拥抱键盘，享受纯粹的编码快感。
*   **100% 积木兼容**：支持所有 Scratch 3.0 的积木，从动作、外观到变量、画笔，应有尽有。
*   **智能表达式解析**：支持复杂数学表达式，自动处理运算符优先级和括号嵌套。
*   **资源管理大师**：轻松导入图片作为造型 (`造型:`) 或背景 (`背景:`)，支持 PNG, JPG, SVG，可自动按比例缩放。
*   **音效指挥家**：导入 MP3 或 WAV 文件 (`音效:`)，为你的项目配上动感音乐。
*   **自带炫酷 IDE**：内置基于 Qt5 的代码编辑器，拥有语法高亮、自动补全、实时语法检查和一键编译功能。
*   **急救编译器**：IDE 未响应？使用独立的急救编译器工具直接编译 .sl 文件。
*   **开箱即用**：提供打包好的可执行文件，无需 Python 环境即可运行。
*   **跨平台运行**：只要有 Python 环境，无论 Windows, macOS 还是 Linux，都能流畅运行。

## v1.3 更新内容

| 类别 | 新增功能 |
|------|----------|
| **表达式解析** | AST 表达式解析器，支持复杂表达式、括号嵌套、运算符优先级 |
| **Bug 修复** | 修复内联代码块 (#code#) 在事件块后断链的问题 |
| **资源管理** | 造型自动按比例缩放功能（可配置开关和最大尺寸） |
| **工具** | 急救编译器 (ScratchLang-Emergency.exe)，IDE 未响应时可用 |
| **打包** | 提供可执行文件 (ScratchLang.exe)，无需 Python 环境 |

### 历史版本

<details>
<summary>v1.2 更新内容</summary>

| 类别 | 新增功能 |
|------|----------|
| **IDE** | 代码折叠、实时语法检查 (500ms 延迟)、编译错误行号定位、错误信息优化 |
| **代码质量** | 魔法字符串提取到 `constants.py`、文件格式验证 (魔数检测) |
| **安全** | 文件内容验证、异常处理改进 |

</details>

<details>
<summary>v1.1 更新内容</summary>

| 类别 | 新增功能 |
|------|----------|
| **IDE** | 自动补全、括号高亮、查找替换 (Ctrl+F/H)、深色/浅色主题切换、最近文件列表、自动保存 |
| **工程化** | 单元测试 (pytest)、类型注解、自定义异常类 |
| **安全** | 路径遍历防护、文件大小限制 (图片10MB/音效20MB) |
| **文档** | 完整语法参考手册 (`docs/SYNTAX.md`) |

</details>

## 安装与运行

### 方式一：使用可执行文件（推荐，无需 Python）

**Windows 用户**可以直接下载打包好的可执行文件：

1. 从 [Releases](https://github.com/moli-ML/scratch-lang/releases) 下载最新版本
2. 解压后运行：
   - `ScratchLang.exe` - 完整 IDE（带图形界面）
   - `ScratchLang-Emergency.exe` - 急救编译器（命令行工具，IDE 未响应时使用）

**急救编译器使用方法：**
- 双击运行 `ScratchLang-Emergency.exe`
- 输入 `.sl` 文件路径
- 输入 `.sb3` 输出路径（可留空自动生成）
- 自动编译完成

### 方式二：从源码运行

**环境要求**: Python 3.7+

#### 1. 克隆项目
```bash
git clone https://github.com/moli-ML/scratch-lang.git
cd scratch-lang
```

#### 2. 安装依赖
```bash
# 创建虚拟环境 (推荐)
python -m venv venv

# 激活环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 开发者额外安装 (可选)
pip install -r requirements-dev.txt
```

#### 3. 启动 IDE
```bash
python main.py
```

#### 4. 运行测试 (可选)
```bash
pytest tests/ -v
```

## 快速上手：画一个正方形

在 IDE 中输入以下代码：

```sl
: 开始

# 我的小猫
当绿旗被点击
  说 "看我画一个正方形！" 2秒
  落笔

  重复 4 次
    移动 100 步
    旋转右 90 度
  结束

  抬笔
  说 "搞定！"
```

按下 **F5** 编译，用 Scratch 或 TurboWarp 打开生成的 `output.sb3` 文件即可运行！

## 语法速查

### 核心概念

| 符号 | 作用 | 示例 |
|------|------|------|
| `: 开始` | 项目开始标记 | `: 开始` |
| `@ 舞台` | 切换到舞台 | `@ 舞台` |
| `# 角色名` | 创建/切换角色 | `# 小猫` |
| `// 注释` | 单行注释 | `// 这是注释` |
| `~变量名` | 引用变量 | `移动 ~速度 步` |

### 资源导入

```sl
造型: images/cat.png
背景: backgrounds/sky.jpg
音效: sounds/meow.mp3
变量: 分数 = 0
列表: 玩家列表
```

### 积木速查表

| 类别 | 语法示例 |
|------|----------|
| **事件** | `当绿旗被点击` `当按下 空格 键` `当收到 消息` |
| **动作** | `移动 10 步` `旋转右 90 度` `移到 0 0` `碰到边缘就反弹` |
| **外观** | `说 "你好" 2秒` `切换造型到 造型2` `将大小设为 50` |
| **声音** | `播放声音 喵` `停止所有声音` `将音量设为 80` |
| **控制** | `等待 1 秒` `重复 10 次 ... 结束` `如果 ... 那么 ... 结束` |
| **变量** | `设置 分数 为 0` `将 金币 增加 10` |
| **画笔** | `落笔` `抬笔` `将笔的颜色设为 #ff0000` |

> 完整语法参考请查看 [docs/SYNTAX.md](docs/SYNTAX.md)

## IDE 功能

| 功能 | 快捷键 | 说明 |
|------|--------|------|
| 编译 | `F5` | 一键编译为 .sb3 文件 |
| 查找 | `Ctrl+F` | 查找文本 |
| 替换 | `Ctrl+H` | 查找并替换 |
| 保存 | `Ctrl+S` | 保存文件 |
| 自动补全 | 输入时自动触发 | 关键字智能提示 |
| 代码折叠 | 点击行号旁 | 折叠重复/如果/重复执行结构 |
| 实时语法检查 | 自动 | 500ms 延迟检查，错误红色下划线 |
| 主题切换 | 视图菜单 | 深色/浅色主题 |
| 自动保存 | - | 每 60 秒自动保存 |

## 项目结构

```
scratch-lang/
├── main.py                      # 程序入口
├── emergency_compile.py         # 急救编译器
├── compiler/                    # 编译器核心
│   ├── parser.py                # 语法解析器
│   ├── builder.py               # SB3 构建器
│   ├── blocks.py                # 积木定义
│   ├── assets.py                # 资源管理
│   ├── constants.py             # 常量定义
│   ├── exceptions.py            # 自定义异常
│   ├── lexer.py                 # 词法分析器
│   ├── expression_parser.py     # 表达式解析器
│   ├── ast_nodes.py             # AST 节点定义
│   └── ast_to_scratch.py        # AST 到 Scratch 转换器
├── ide/                         # IDE 界面
│   ├── mainwindow.py            # 主窗口
│   ├── editor.py                # 代码编辑器
│   └── highlighter.py           # 语法高亮
├── tests/                       # 单元测试
├── docs/                        # 文档
│   └── SYNTAX.md                # 语法参考
├── examples/                    # 示例代码
│   └── demo.sl
├── dist/                        # 打包输出
│   ├── ScratchLang.exe          # IDE 可执行文件
│   └── ScratchLang-Emergency.exe # 急救编译器
└── .mailmap                     # Git 贡献者映射
```

## 开发进度

| 类别 | 完成率 |
|------|--------|
| 工程化 | 100% |
| 代码质量 | 73% |
| IDE 功能 | 100% |
| 表达式解析 | 100% |
| 功能完整性 | 100% |
| 文档 | 83% |
| 安全 | 100% |
| Bug 修复 | 100% |
| **总计** | **95%** |

> 详细进度请查看 [ISSUES.md](ISSUES.md)

## 待实现功能

- [x] ~~复杂表达式支持~~ (v1.3 已完成)
- [x] ~~内联代码块支持~~ (v1.3 已完成)
- [ ] 自定义积木 (自制积木) 完善
- [ ] 更多扩展积木支持 (音乐、视频侦测等)
- [ ] 云变量完善
- [ ] 多行字符串支持
- [ ] 块注释 `/* */` 支持

## 常见问题

**Q: 编译时提示"文件不存在"怎么办？**
A: 确保资源路径正确，推荐使用 IDE 的"插入"功能自动处理路径。

**Q: 可以分享给没有 ScratchLang 的朋友吗？**
A: 可以！生成的 `.sb3` 是标准 Scratch 项目文件，可用 Scratch 或 TurboWarp 打开。

**Q: 支持哪些图片/音频格式？**
A: 图片支持 PNG、JPG、SVG (最大 10MB)，音频支持 MP3、WAV (最大 20MB)。文件格式会通过魔数验证。

**Q: 实时语法检查怎么用？**
A: 输入代码后 500ms 自动检查，错误会以红色下划线标记，详细信息显示在输出窗口。

**Q: IDE 未响应怎么办？**
A: 使用急救编译器 `ScratchLang-Emergency.exe`，它是独立的命令行工具，可以直接编译 .sl 文件。

**Q: 如何启用造型自动缩放？**
A: 在代码中使用 `ScratchLangParser(auto_scale_costumes=True, max_costume_size=480)`，或等待后续版本的 IDE 配置选项。

**Q: 复杂表达式怎么写？**
A: 支持括号和运算符优先级，例如：`设置 ~结果 为 (~分数 + 10) * 2`，会自动解析为正确的积木嵌套。

## 贡献指南

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 运行测试 (`pytest tests/ -v`)
4. 提交更改 (`git commit -m 'Add AmazingFeature'`)
5. 推送分支 (`git push origin feature/AmazingFeature`)
6. 发起 Pull Request

## 许可证

本项目基于 [MIT 许可证](LICENSE) 开源。
