# Repository Guidelines

## 项目结构与模块组织
- `main.py` — IDE 入口（启动 PyQt5 应用）。
- `ide/` — 界面与交互：`mainwindow.py`、`editor.py`、`highlighter.py`。
- `compiler/` — 语言内核：`parser.py`、`blocks.py`、`builder.py`、`assets.py`。
- `examples/` — 示例程序（如 `demo.sl`）。
- `requirements.txt` — 依赖（PyQt5、Pillow）。

## 构建、测试与开发命令
- 创建环境（Windows）：`python -m venv .venv && .venv\\Scripts\\activate`
- 安装依赖：`pip install -r requirements.txt`
- 运行 IDE：`python main.py`
- 可选检查：`ruff .`/`flake8`
- 可选格式化：`black . && isort .`

## 代码风格与命名规范
- Python 3.7+；4 空格缩进；UTF‑8。
- 遵循 PEP 8；新/改公共函数补充类型注解。
- 命名：模块 `snake_case.py`；类 `PascalCase`；函数/变量 `snake_case`。
- Docstring 简洁：一行摘要 + 必要补充。
- UI 信号/槽靠近控件声明；编译器逻辑置于 `compiler/` 且不依赖 UI。

## 测试指南
- 推荐 `pytest`；用 `tests/` 镜像源码目录组织测试。
- 文件：`tests/test_<module>.py`；用例：`test_<behavior>()`。
- 覆盖重点：解析器、积木语义、构建结果。
- 运行：`pytest -q`（先安装 `pytest`）。

## 提交与合并请求规范
- 提交：祈使句主题（≤72 字符），正文说明动机与影响。
- 建议格式：`feat(compiler): add loop unrolling pass`。
- PR：描述、动机、UI 截图（如适用）、复现步骤；用 `Fixes #<id>` 关联问题。
- 保持单一职责；确保 CI 通过（若已配置）。

## 安全与配置提示
- PyQt5 需 GUI 环境；避免在 UI 线程阻塞。
- 不加载不可信 `.sl`；在解析器中校验输入。
- 资源放在 `compiler/assets/` 或 `ide/` 子目录，使用相对路径。

## Agent 协作说明
- 遵循本指南；最小化改动并对齐现有风格；不确定时参考 `ide/` 与 `compiler/` 的既有模式。
