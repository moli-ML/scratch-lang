"""
SB3项目构建器
"""
import json
import zipfile
import random
import string
from typing import Dict, List, Any, Optional, Union
from urllib.parse import quote
from .assets import AssetManager

# 类型别名
SpriteData = Dict[str, Any]
BlockData = Dict[str, Any]
ProjectData = Dict[str, Any]


class SB3Builder:
    """SB3 项目文件构建器

    用于构建 Scratch 3.0 项目文件 (.sb3)，支持添加角色、舞台、
    积木、变量、列表、造型、音效等。
    """

    def __init__(self, auto_scale_costumes: bool = False, max_costume_size: int = 480) -> None:
        self.project = {
            "targets": [],
            "monitors": [],
            "extensions": [],
            "extensionURLs": {},
            "meta": {
                "semver": "3.0.0",
                "vm": "0.2.0",
                "agent": "ScratchLang Compiler v1.0"
            }
        }
        self.asset_manager = AssetManager(auto_scale_costumes, max_costume_size)
        self.current_sprite = None
        self.stage = None
        self.variables = {}
        self.lists = {}
        self.broadcasts = {}
        self.has_custom_costume = False
        
    def add_sprite(self, name: str, is_stage: bool = False) -> SpriteData:
        """添加角色或舞台

        Args:
            name: 角色名称
            is_stage: 是否为舞台

        Returns:
            SpriteData: 创建的角色/舞台数据
        """
        sprite = {
            "isStage": is_stage,
            "name": "Stage" if is_stage else name,
            "variables": {},
            "lists": {},
            "broadcasts": {},
            "blocks": {},
            "comments": {},
            "currentCostume": 0,
            "costumes": [],
            "sounds": [],
            "volume": 100,
            "layerOrder": len(self.project["targets"])
        }
        
        if is_stage:
            sprite.update({
                "tempo": 60,
                "videoTransparency": 50,
                "videoState": "on",
                "textToSpeechLanguage": None
            })
            self.stage = sprite
        else:
            sprite.update({
                "visible": True,
                "x": 0,
                "y": 0,
                "size": 100,
                "direction": 90,
                "draggable": False,
                "rotationStyle": "all around"
            })
        
        self.project["targets"].append(sprite)
        self.current_sprite = sprite
        self.has_custom_costume = False
        return sprite
    
    def switch_to_stage(self) -> SpriteData:
        """切换到舞台

        Returns:
            SpriteData: 舞台数据
        """
        if not self.stage:
            self.add_sprite("Stage", is_stage=True)

        self.current_sprite = self.stage
        self.has_custom_costume = len(self.stage["costumes"]) > 0
        print("[切换到舞台]")
        return self.current_sprite
    
    def add_costume(self, filepath: str, is_backdrop: bool = False) -> None:
        """添加造型或背景

        Args:
            filepath: 图片文件路径
            is_backdrop: 是否为背景
        """
        if not self.has_custom_costume and len(self.current_sprite["costumes"]) > 0:
            self.current_sprite["costumes"] = []
            print(f"🗑️  清除默认{'背景' if is_backdrop else '造型'}")
        
        costume = self.asset_manager.add_image(filepath)
        
        if is_backdrop:
            costume["name"] = f"backdrop{len(self.current_sprite['costumes']) + 1}"
        else:
            costume["name"] = f"costume{len(self.current_sprite['costumes']) + 1}"
        
        costume.update({
            "rotationCenterX": 0,
            "rotationCenterY": 0,
        })
        
        if costume["dataFormat"] in ["png", "jpg"]:
            costume["bitmapResolution"] = 1
        
        self.current_sprite["costumes"].append(costume)
        self.has_custom_costume = True
    
    def add_backdrop(self, filepath: str) -> None:
        """添加背景（舞台专用）

        Args:
            filepath: 背景图片文件路径
        """
        if not self.current_sprite or not self.current_sprite["isStage"]:
            print("⚠️ 警告: 只有舞台可以添加背景")
            return
        
        self.add_costume(filepath, is_backdrop=True)
    
    def add_sound(self, filepath: str) -> None:
        """添加音效

        Args:
            filepath: 音效文件路径
        """
        sound = self.asset_manager.add_sound(filepath)
        self.current_sprite["sounds"].append(sound)
    
    def finalize_sprite(self) -> None:
        """完成角色设置，如果没有造型则添加默认造型"""
        if len(self.current_sprite["costumes"]) == 0:
            if self.current_sprite["isStage"]:
                default_bg = self.asset_manager.create_default_backdrop()
                self.current_sprite["costumes"].append(default_bg)
                print(f"[舞台] 使用默认背景")
            else:
                default_costume = self.asset_manager.create_default_svg(
                    self.current_sprite["name"]
                )
                self.current_sprite["costumes"].append(default_costume)
                print(f"[{self.current_sprite['name']}] 使用默认造型")
        else:
            costume_type = "背景" if self.current_sprite["isStage"] else "造型"
            print(f"[{self.current_sprite['name']}] {len(self.current_sprite['costumes'])} 个{costume_type}")
    
    def generate_id(self, length: int = 20) -> str:
        """生成唯一ID

        Args:
            length: ID 长度，默认 20

        Returns:
            str: 随机生成的 ID
        """
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def add_variable(self, name: str, value: Union[int, float, str] = 0) -> str:
        """添加变量

        Args:
            name: 变量名
            value: 初始值

        Returns:
            str: 变量 ID
        """
        # 检查是否已存在同名变量
        for var_id, var_data in self.current_sprite.get("variables", {}).items():
            if var_data[0] == name:
                return var_id
        if self.stage and self.current_sprite != self.stage:
            for var_id, var_data in self.stage.get("variables", {}).items():
                if var_data[0] == name:
                    return var_id

        var_id = self.generate_id()
        self.current_sprite["variables"][var_id] = [name, value]
        return var_id

    def add_cloud_variable(self, name: str, value: Union[int, float] = 0) -> str:
        """添加云变量

        Args:
            name: 变量名（会自动添加☁前缀）
            value: 初始值（只能是数字）

        Returns:
            str: 变量 ID
        """
        var_id = self.generate_id()
        cloud_name = f"☁ {name}" if not name.startswith("☁") else name
        # 云变量存储格式: [name, value, True] 第三个参数表示是云变量
        self.current_sprite["variables"][var_id] = [cloud_name, value, True]
        return var_id

    def add_list(self, name: str, items: Optional[List[Any]] = None) -> str:
        """添加列表

        Args:
            name: 列表名
            items: 初始项目

        Returns:
            str: 列表 ID
        """
        list_id = self.generate_id()
        self.current_sprite["lists"][list_id] = [name, items or []]
        return list_id

    def add_broadcast(self, name: str) -> str:
        """添加广播

        Args:
            name: 广播名称

        Returns:
            str: 广播 ID
        """
        if name not in self.broadcasts:
            broadcast_id = self.generate_id()
            self.broadcasts[name] = broadcast_id
        return self.broadcasts[name]

    def add_extension(self, extension_name: str) -> None:
        """添加扩展

        Args:
            extension_name: 扩展名称 (如 "music", "pen")
        """
        if extension_name not in self.project["extensions"]:
            self.project["extensions"].append(extension_name)

    def add_custom_extension_code(self, extension_id: str, js_code: str) -> None:
        """添加自定义扩展 JS 代码（TurboWarp 格式）

        Args:
            extension_id: 扩展 ID
            js_code: JavaScript 代码
        """
        # 将用户代码包装为 Scratch 扩展格式，创建可执行的积木
        class_name = extension_id.replace('inlinecode', 'InlineCode')
        wrapped_code = f"""class {class_name} {{
  getInfo() {{
    return {{
      id: '{extension_id}',
      name: 'Inline Code',
      blocks: [
        {{
          opcode: 'run',
          blockType: Scratch.BlockType.COMMAND,
          text: 'run inline code'
        }}
      ]
    }};
  }}

  run(args) {{
    {js_code}
  }}
}}

Scratch.extensions.register(new {class_name}());"""

        # 将 JS 代码编码为 data URL
        encoded_js = quote(wrapped_code, safe='')
        data_url = f"data:application/javascript,{encoded_js}"
        self.project["extensionURLs"][extension_id] = data_url

    def add_block(
        self,
        opcode: str,
        inputs: Optional[Dict[str, Any]] = None,
        fields: Optional[Dict[str, Any]] = None,
        parent: Optional[str] = None,
        top_level: bool = False
    ) -> str:
        """添加积木

        Args:
            opcode: 积木操作码
            inputs: 输入参数
            fields: 字段参数
            parent: 父积木 ID
            top_level: 是否为顶层积木

        Returns:
            str: 积木 ID
        """
        block_id = self.generate_id()
        block = {
            "opcode": opcode,
            "next": None,
            "parent": parent,
            "inputs": inputs or {},
            "fields": fields or {},
            "shadow": False,
            "topLevel": top_level
        }

        if top_level:
            block["x"] = 50 + (len(self.current_sprite["blocks"]) % 3) * 300
            block["y"] = 50 + (len(self.current_sprite["blocks"]) // 3) * 200

        self.current_sprite["blocks"][block_id] = block

        # 自动设置输入块的 parent
        for inp_name, inp_val in (inputs or {}).items():
            if isinstance(inp_val, list) and len(inp_val) >= 2:
                child_id = inp_val[1]
                if isinstance(child_id, str) and child_id in self.current_sprite["blocks"]:
                    self.current_sprite["blocks"][child_id]["parent"] = block_id

        return block_id
    
    def add_shadow_block(self, opcode: str, fields: Dict[str, Any]) -> str:
        """添加阴影积木（shadow block）

        Shadow blocks 是 Scratch 中用于下拉菜单选项的特殊积木

        Args:
            opcode: 积木操作码
            fields: 字段参数

        Returns:
            str: 阴影积木 ID
        """
        shadow_id = self.generate_id()
        shadow_block = {
            "opcode": opcode,
            "next": None,
            "parent": None,
            "inputs": {},
            "fields": fields,
            "shadow": True,
            "topLevel": False
        }
        self.current_sprite["blocks"][shadow_id] = shadow_block
        return shadow_id
    
    def save(self, filename: str) -> None:
        """保存为 sb3 文件

        Args:
            filename: 输出文件路径
        """
        for target in self.project["targets"]:
            if len(target["costumes"]) == 0:
                self.current_sprite = target
                self.finalize_sprite()
        
        with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zf:
            project_json = json.dumps(self.project, ensure_ascii=False, indent=2)
            zf.writestr('project.json', project_json)
            
            for asset_name, asset_data in self.asset_manager.assets.items():
                zf.writestr(asset_name, asset_data)