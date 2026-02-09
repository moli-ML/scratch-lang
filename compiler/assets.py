"""
资源文件管理
"""
import hashlib
import os
from typing import Dict, Any, Optional
from PIL import Image
import io
import struct
from .constants import (
    MAX_IMAGE_SIZE, MAX_SOUND_SIZE,
    SUPPORTED_IMAGE_FORMATS, SUPPORTED_SOUND_FORMATS
)


def validate_image_format(filepath: str, data: bytes) -> bool:
    """验证图片文件格式是否有效

    Args:
        filepath: 文件路径
        data: 文件数据

    Returns:
        bool: 格式是否有效
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext not in SUPPORTED_IMAGE_FORMATS:
        return False

    # 检查文件头魔数
    if ext == '.png':
        # PNG: 89 50 4E 47 0D 0A 1A 0A
        return data[:8] == b'\x89PNG\r\n\x1a\n'
    elif ext in ('.jpg', '.jpeg'):
        # JPEG: FF D8 FF
        return data[:3] == b'\xff\xd8\xff'
    elif ext == '.gif':
        # GIF: GIF87a 或 GIF89a
        return data[:6] in (b'GIF87a', b'GIF89a')
    elif ext == '.bmp':
        # BMP: BM
        return data[:2] == b'BM'
    elif ext == '.svg':
        # SVG: 检查是否包含 <svg 标签
        try:
            text = data.decode('utf-8', errors='ignore')
            return '<svg' in text.lower()
        except:
            return False

    return True


def _get_wav_audio_info(data: bytes) -> tuple:
    """解析 WAV 文件头，获取采样率和采样数

    Args:
        data: WAV 文件数据

    Returns:
        tuple: (sample_rate, sample_count) 或 (None, None) 如果解析失败
    """
    try:
        # WAV 文件结构:
        # 0-3: "RIFF"
        # 4-7: 文件大小
        # 8-11: "WAVE"
        # 12-15: "fmt "
        # 16-19: fmt chunk size
        # 20-21: Audio format (1 = PCM)
        # 22-23: Number of channels
        # 24-27: Sample rate
        # 28-31: Byte rate
        # 32-33: Block align
        # 34-35: Bits per sample

        if len(data) < 44:
            return None, None

        # 验证是 WAV 文件
        if data[:4] != b'RIFF' or data[8:12] != b'WAVE':
            return None, None

        # 读取 fmt chunk
        fmt_chunk_size = struct.unpack('<I', data[16:20])[0]
        num_channels = struct.unpack('<H', data[22:24])[0]
        sample_rate = struct.unpack('<I', data[24:28])[0]
        bits_per_sample = struct.unpack('<H', data[34:36])[0]

        # 查找 data chunk
        pos = 12 + 8 + fmt_chunk_size  # 跳过 RIFF header 和 fmt chunk
        while pos < len(data) - 8:
            chunk_id = data[pos:pos+4]
            chunk_size = struct.unpack('<I', data[pos+4:pos+8])[0]
            if chunk_id == b'data':
                # data chunk 找到，计算采样数
                data_size = min(chunk_size, len(data) - pos - 8)
                bytes_per_sample = (bits_per_sample // 8) * num_channels
                if bytes_per_sample > 0:
                    sample_count = data_size // bytes_per_sample
                    return sample_rate, sample_count
            pos += 8 + chunk_size

        return None, None
    except Exception:
        return None, None


def validate_sound_format(filepath: str, data: bytes) -> bool:
    """验证音频文件格式是否有效

    Args:
        filepath: 文件路径
        data: 文件数据

    Returns:
        bool: 格式是否有效
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext not in SUPPORTED_SOUND_FORMATS:
        return False

    # 检查文件头魔数
    if ext == '.mp3':
        # MP3: ID3 标签或 FF FB/FF FA/FF F3/FF F2 帧同步
        if data[:3] == b'ID3':
            return True
        if len(data) >= 2 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0:
            return True
        return False
    elif ext == '.wav':
        # WAV: RIFF....WAVE
        return data[:4] == b'RIFF' and data[8:12] == b'WAVE'
    elif ext == '.ogg':
        # OGG: OggS
        return data[:4] == b'OggS'

    return True


class AssetManager:
    """资源文件管理器

    管理 Scratch 项目中的图片和音效资源。
    """

    def __init__(self, auto_scale_costumes: bool = False, max_costume_size: int = 480) -> None:
        self.assets: Dict[str, bytes] = {}
        self.auto_scale_costumes = auto_scale_costumes
        self.max_costume_size = max_costume_size
        
    def add_image(self, filepath: str) -> Dict[str, Any]:
        """添加图片资源

        Args:
            filepath: 图片文件路径

        Returns:
            Dict: 包含资源信息的字典

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件过大或格式无效
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"图片文件不存在: {filepath}")

        # 检查文件扩展名
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in SUPPORTED_IMAGE_FORMATS:
            raise ValueError(f"不支持的图片格式: {ext}，支持的格式: {', '.join(SUPPORTED_IMAGE_FORMATS)}")

        # 检查文件大小
        file_size = os.path.getsize(filepath)
        if file_size > MAX_IMAGE_SIZE:
            raise ValueError(f"图片文件过大: {file_size / 1024 / 1024:.1f}MB，最大允许 {MAX_IMAGE_SIZE / 1024 / 1024:.0f}MB")

        with open(filepath, 'rb') as f:
            data = f.read()

        # 验证文件内容格式
        if not validate_image_format(filepath, data):
            raise ValueError(f"图片文件格式无效或已损坏: {filepath}")

        rotation_center = None
        if ext == '.svg':
            final_data = data
            format_ext = 'svg'
            # 解析 SVG 尺寸计算 rotationCenter
            rotation_center = self._get_svg_rotation_center(data)
        else:
            # 使用PIL转换
            try:
                img = Image.open(io.BytesIO(data))

                # 自动缩放
                if self.auto_scale_costumes:
                    max_dim = max(img.width, img.height)
                    if max_dim > self.max_costume_size:
                        scale = self.max_costume_size / max_dim
                        new_width = int(img.width * scale)
                        new_height = int(img.height * scale)
                        img = img.resize((new_width, new_height), Image.LANCZOS)

                # 计算 rotationCenter（图片中心）
                rotation_center = (img.width // 2, img.height // 2)
                output = io.BytesIO()
                img.save(output, format='PNG')
                final_data = output.getvalue()
                format_ext = 'png'
            except Exception as e:
                raise ValueError(f"无法处理图片文件: {filepath}，错误: {e}")

        md5 = hashlib.md5(final_data).hexdigest()
        filename = f"{md5}.{format_ext}"

        self.assets[filename] = final_data

        result = {
            "assetId": md5,
            "name": os.path.basename(filepath),
            "md5ext": filename,
            "dataFormat": format_ext
        }

        if rotation_center:
            result["rotationCenterX"] = rotation_center[0]
            result["rotationCenterY"] = rotation_center[1]

        return result

    def _get_svg_rotation_center(self, data: bytes) -> tuple:
        """从 SVG 数据中解析尺寸并计算 rotationCenter

        Args:
            data: SVG 文件数据

        Returns:
            tuple: (centerX, centerY)
        """
        import re
        try:
            text = data.decode('utf-8', errors='ignore')
            # 尝试解析 width 和 height 属性
            width_match = re.search(r'<svg[^>]*\swidth=["\']?(\d+(?:\.\d+)?)', text, re.IGNORECASE)
            height_match = re.search(r'<svg[^>]*\sheight=["\']?(\d+(?:\.\d+)?)', text, re.IGNORECASE)

            if width_match and height_match:
                width = float(width_match.group(1))
                height = float(height_match.group(1))
                return (int(width / 2), int(height / 2))

            # 尝试解析 viewBox 属性
            viewbox_match = re.search(r'viewBox=["\']?\s*[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)', text, re.IGNORECASE)
            if viewbox_match:
                width = float(viewbox_match.group(1))
                height = float(viewbox_match.group(2))
                return (int(width / 2), int(height / 2))

        except Exception:
            pass

        # 默认值
        return (50, 50)
    
    def add_sound(self, filepath: str) -> Dict[str, Any]:
        """添加音效资源

        Args:
            filepath: 音效文件路径

        Returns:
            Dict: 包含资源信息的字典

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件过大或格式无效
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"音效文件不存在: {filepath}")

        # 检查文件扩展名
        ext_with_dot = os.path.splitext(filepath)[1].lower()
        if ext_with_dot not in SUPPORTED_SOUND_FORMATS:
            raise ValueError(f"不支持的音频格式: {ext_with_dot}，支持的格式: {', '.join(SUPPORTED_SOUND_FORMATS)}")

        # 检查文件大小
        file_size = os.path.getsize(filepath)
        if file_size > MAX_SOUND_SIZE:
            raise ValueError(f"音效文件过大: {file_size / 1024 / 1024:.1f}MB，最大允许 {MAX_SOUND_SIZE / 1024 / 1024:.0f}MB")

        with open(filepath, 'rb') as f:
            data = f.read()

        # 验证文件内容格式
        if not validate_sound_format(filepath, data):
            raise ValueError(f"音频文件格式无效或已损坏: {filepath}")

        ext = ext_with_dot.replace('.', '')
        md5 = hashlib.md5(data).hexdigest()
        filename = f"{md5}.{ext}"

        self.assets[filename] = data

        # 尝试获取音频文件的采样信息
        sample_rate = 48000
        sample_count = 0

        if ext == 'wav':
            wav_rate, wav_count = _get_wav_audio_info(data)
            if wav_rate is not None:
                sample_rate = wav_rate
                sample_count = wav_count

        return {
            "assetId": md5,
            "name": os.path.basename(filepath),
            "md5ext": filename,
            "dataFormat": ext,
            "rate": sample_rate,
            "sampleCount": sample_count
        }
    
    def create_default_svg(self, name, color="#FF6680"):
        """创建默认SVG造型"""
        svg = f'''<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <circle cx="50" cy="50" r="40" fill="{color}"/>
  <text x="50" y="55" font-size="12" text-anchor="middle" fill="white">{name}</text>
</svg>'''
        data = svg.encode('utf-8')
        md5 = hashlib.md5(data).hexdigest()
        filename = f"{md5}.svg"
        self.assets[filename] = data
        
        return {
            "assetId": md5,
            "name": "costume1",
            "md5ext": filename,
            "dataFormat": "svg",
            "rotationCenterX": 50,
            "rotationCenterY": 50
        }
    
    def create_default_backdrop(self, color="#FFFFFF"):
        """创建默认背景（白色）"""
        svg = f'''<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="480" height="360">
  <rect width="480" height="360" fill="{color}"/>
</svg>'''
        data = svg.encode('utf-8')
        md5 = hashlib.md5(data).hexdigest()
        filename = f"{md5}.svg"
        self.assets[filename] = data
        
        return {
            "assetId": md5,
            "name": "backdrop1",
            "md5ext": filename,
            "dataFormat": "svg",
            "rotationCenterX": 240,
            "rotationCenterY": 180
        }