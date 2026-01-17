# 测试说明

## 安装测试依赖

```bash
pip install -r requirements-dev.txt
```

或单独安装 pytest：

```bash
pip install pytest
```

## 运行所有测试

```bash
# 在项目根目录运行
pytest tests/ -v

# 或使用 Python 模块方式
python -m pytest tests/ -v
```

## 运行特定测试文件

```bash
# 测试解析器
pytest tests/test_parser.py -v

# 测试积木定义
pytest tests/test_blocks.py -v

# 测试构建器
pytest tests/test_builder.py -v

# 测试扩展功能
pytest tests/test_extensions.py -v

# 测试异常处理
pytest tests/test_exceptions.py -v
```

## 测试覆盖率

```bash
pytest tests/ --cov=compiler --cov-report=html
```

## 测试文件说明

### test_parser.py
- 基础解析测试（空代码、注释、开始标记）
- 角色和舞台测试
- 事件积木测试（绿旗、按键）
- 动作积木测试（移动、旋转、坐标）
- 控制积木测试（重复、如果、重复执行）
- 变量测试
- 比较运算符测试（>、<、>=、<=）
- 安全测试（路径遍历攻击）
- 新功能测试：
  - 块注释 `/* */`
  - 多行字符串 `"""..."""`
  - 转义字符 `\n \t \r`
  - JS 代码块 `#code# ... #end#`

### test_extensions.py
- 扩展管理器测试
  - 从 getInfo() 提取扩展 ID
  - 从简单 id 字段提取扩展 ID
  - 无法提取时返回 None
- 扩展导入测试
  - 提取中文导入语句 `导入扩展: "file.js"`
  - 提取英文导入语句 `import extension: "file.js"`
  - 解析包含扩展导入的完整代码
  - 导入不存在文件时抛出异常

### test_blocks.py
- 积木定义正则表达式测试
- 积木参数匹配测试

### test_builder.py
- SB3 项目构建测试
- 角色添加测试
- 积木创建测试

### test_exceptions.py
- 自定义异常类测试
- 异常继承关系测试

## 新增测试统计

| 测试文件 | 新增测试 | 说明 |
|---------|---------|------|
| test_extensions.py | 7 个 | 全新文件，测试扩展导入功能 |
| test_parser.py | 4 个 | 新增 TestNewFeatures 类 |
| **总计** | **11 个** | **覆盖所有新功能** |

## 测试要点

1. **块注释测试**：验证 `/* */` 注释被正确移除且保留行号
2. **多行字符串测试**：验证 `"""..."""` 转换为单行字符串
3. **转义字符测试**：验证 `\n \t \r \\ \" \'` 正确处理
4. **JS 代码块测试**：验证 `#code# ... #end#` 块被提取
5. **扩展导入测试**：验证导入语法解析和 JS 文件加载
6. **扩展 ID 提取测试**：验证从 JS 代码中提取扩展 ID

## 待办事项

- [ ] 添加自定义积木测试
- [ ] 添加云变量测试
- [ ] 添加音乐扩展积木测试
- [ ] 添加英文语法测试
- [ ] 提高测试覆盖率到 90% 以上
