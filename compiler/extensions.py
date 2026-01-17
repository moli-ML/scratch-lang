"""
自定义扩展支持模块

允许用户定义自己的 Scratch 扩展，支持自定义积木和 JavaScript 代码。
"""
import json
import re
from typing import Dict, List, Any, Optional


class ExtensionBlock:
    """扩展积木定义"""

    def __init__(self, opcode: str, text: str, block_type: str = "command",
                 arguments: Optional[Dict] = None):
        """
        Args:
            opcode: 积木操作码
            text: 积木显示文本，使用 [参数名] 表示参数
            block_type: 积木类型 (command, reporter, boolean, hat)
            arguments: 参数定义 {参数名: {type, default}}
        """
        self.opcode = opcode
        self.text = text
        self.block_type = block_type
        self.arguments = arguments or {}


class CustomExtension:
    """自定义扩展"""

    def __init__(self, extension_id: str, name: str):
        """
        Args:
            extension_id: 扩展 ID
            name: 扩展名称
        """
        self.extension_id = extension_id
        self.name = name
        self.blocks: List[ExtensionBlock] = []
        self.js_code: str = ""

    def add_block(self, block: ExtensionBlock):
        """添加积木定义"""
        self.blocks.append(block)

    def set_js_code(self, code: str):
        """设置 JavaScript 代码"""
        self.js_code = code

    def to_scratch_extension(self) -> Dict[str, Any]:
        """转换为 Scratch 扩展格式"""
        return {
            "id": self.extension_id,
            "name": self.name,
            "blocks": [
                {
                    "opcode": block.opcode,
                    "blockType": block.block_type,
                    "text": block.text,
                    "arguments": block.arguments
                }
                for block in self.blocks
            ]
        }


class ExtensionManager:
    """扩展管理器"""

    def __init__(self):
        self.extensions: Dict[str, CustomExtension] = {}

    def register_extension(self, extension: CustomExtension):
        """注册扩展"""
        self.extensions[extension.extension_id] = extension

    def get_extension(self, extension_id: str) -> Optional[CustomExtension]:
        """获取扩展"""
        return self.extensions.get(extension_id)

    def parse_extension_definition(self, code: str) -> Optional[CustomExtension]:
        """从代码中解析扩展定义

        扩展定义格式:
        #extension myext "我的扩展"
            #block myblock "执行 [参数1] 操作"
            #reporter myreporter "获取 [名称] 的值"
        #endextension

        Args:
            code: 扩展定义代码

        Returns:
            CustomExtension 或 None
        """
        # 匹配扩展定义
        ext_match = re.search(
            r'#extension\s+(\w+)\s+"([^"]+)"(.*?)#endextension',
            code, re.DOTALL
        )
        if not ext_match:
            return None

        ext_id = ext_match.group(1)
        ext_name = ext_match.group(2)
        ext_body = ext_match.group(3)

        extension = CustomExtension(ext_id, ext_name)

        # 解析积木定义
        block_pattern = r'#(block|reporter|boolean|hat)\s+(\w+)\s+"([^"]+)"'
        for match in re.finditer(block_pattern, ext_body):
            block_type = match.group(1)
            opcode = match.group(2)
            text = match.group(3)

            # 解析参数
            arguments = {}
            arg_pattern = r'\[(\w+)\]'
            for arg_match in re.finditer(arg_pattern, text):
                arg_name = arg_match.group(1)
                arguments[arg_name] = {
                    "type": "string",
                    "defaultValue": ""
                }

            block = ExtensionBlock(
                opcode=f"{ext_id}_{opcode}",
                text=text,
                block_type=block_type,
                arguments=arguments
            )
            extension.add_block(block)

        return extension

    def get_all_extensions(self) -> List[CustomExtension]:
        """获取所有已注册的扩展"""
        return list(self.extensions.values())

    def parse_js_extension(self, js_code: str) -> Optional[str]:
        """从 JavaScript 代码中提取扩展 ID

        Args:
            js_code: JavaScript 扩展代码

        Returns:
            扩展 ID 或 None
        """
        # 尝试匹配常见的扩展 ID 定义模式
        patterns = [
            r"getInfo\s*\(\s*\)\s*{[^}]*id\s*:\s*['\"]([^'\"]+)['\"]",
            r"id\s*:\s*['\"]([^'\"]+)['\"]",
            r"extensionId\s*=\s*['\"]([^'\"]+)['\"]",
        ]

        for pattern in patterns:
            match = re.search(pattern, js_code, re.DOTALL)
            if match:
                return match.group(1)

        return None


# 全局扩展管理器实例
extension_manager = ExtensionManager()
