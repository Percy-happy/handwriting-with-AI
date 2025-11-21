"""
手写体生成模块
负责将文本转换为手写体图像
"""
import logging
import os
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HandwritingGenerator:
    """手写体生成器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.font_size = config.get("font_size", 12)
        self.line_spacing = config.get("line_spacing", 1.5)
        self.margin = config.get("margin", 10)
        self.effect_style = config.get("effect_style", "limited")
        
        # A5尺寸（像素，假设300 DPI）
        self.a5_width = 1748  # 210mm * 300 / 25.4
        self.a5_height = 2480  # 297mm * 300 / 25.4
    
    def generate_handwriting(self, text: str, **kwargs) -> Optional[Image.Image]:
        """生成手写体图像
        
        Args:
            text: 要转换的文本
            **kwargs: 额外参数
            
        Returns:
            手写体图像或None
        """
        raise NotImplementedError("子类必须实现generate_handwriting方法")
    
    def save_image(self, image: Image.Image, output_path: str) -> bool:
        """保存图像到文件
        
        Args:
            image: 图像对象
            output_path: 输出文件路径
            
        Returns:
            是否保存成功
        """
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            image.save(output_path)
            logger.info(f"图像已保存到: {output_path}")
            return True
        except Exception as e:
            logger.error(f"保存图像失败: {e}")
            return False
    
    def update_config(self, **kwargs):
        """更新配置
        
        Args:
            **kwargs: 要更新的配置项
        """
        for key, value in kwargs.items():
            if key in self.__dict__:
                self.__dict__[key] = value
            if key in self.config:
                self.config[key] = value

class PillowHandwritingGenerator(HandwritingGenerator):
    """使用Pillow实现的手写体生成器（基本版本）"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._font_cache = {}
    
    def _get_font(self, size: int) -> Optional[ImageFont.FreeTypeFont]:
        """获取字体对象
        
        Args:
            size: 字体大小
            
        Returns:
            字体对象或None
        """
        # 尝试使用系统字体
        font_names = [
            "Ma Shan Zheng",  # 马善政，一种手写风格的中文字体
            "ZCOOL QingKe HuangYou",  # 站酷庆科黄油体
            "ZCOOL XiaoWei",  # 站酷小薇体
            "SimHei",  # 黑体
            "WenQuanYi Micro Hei",  # 文泉驿微米黑
            "Heiti TC"  # 黑体（macOS）
        ]
        
        # 尝试获取字体
        for font_name in font_names:
            try:
                font = ImageFont.truetype(font_name, size)
                return font
            except (OSError, IOError):
                continue
        
        # 如果找不到指定字体，使用默认字体
        logger.warning("找不到合适的中文字体，使用默认字体")
        return ImageFont.load_default()
    
    def generate_handwriting(self, text: str, **kwargs) -> Optional[Image.Image]:
        """生成手写体图像
        
        Args:
            text: 要转换的文本
            **kwargs: 额外参数
            
        Returns:
            手写体图像或None
        """
        try:
            # 获取参数
            font_size = kwargs.get("font_size", self.font_size)
            line_spacing = kwargs.get("line_spacing", self.line_spacing)
            margin = kwargs.get("margin", self.margin)
            
            # 获取字体
            font = self._get_font(font_size)
            
            # 创建图像（A5横版）
            # 计算文本区域大小
            text_area_width = self.a5_width - 2 * margin
            text_area_height = self.a5_height - 2 * margin
            
            # 分割文本为行
            lines = []
            words = text.split('\n')
            
            for paragraph in words:
                if not paragraph:  # 处理空行
                    lines.append("")
                    continue
                
                # 简单的行分割，根据文本区域宽度
                current_line = ""
                for char in paragraph:
                    # 测试添加字符后的宽度
                    test_line = current_line + char
                    test_width = font.getsize(test_line)[0]
                    
                    if test_width > text_area_width:
                        # 如果超出宽度，保存当前行并开始新行
                        lines.append(current_line)
                        current_line = char
                    else:
                        current_line = test_line
                
                # 添加最后一行
                if current_line:
                    lines.append(current_line)
            
            # 计算实际需要的高度
            line_height = font.getsize("测试")[1]
            actual_text_height = int(len(lines) * line_height * line_spacing)
            
            # 创建图像（使用白色背景）
            image = Image.new('RGB', (self.a5_width, self.a5_height), color='white')
            draw = ImageDraw.Draw(image)
            
            # 计算起始位置（垂直居中）
            start_y = margin + (text_area_height - actual_text_height) // 2
            
            # 绘制文本
            for i, line in enumerate(lines):
                # 添加一些随机偏移，模拟手写效果
                import random
                offset_x = margin + random.randint(-2, 2)
                offset_y = start_y + i * line_height * line_spacing + random.randint(-1, 1)
                
                # 根据效果风格调整
                if self.effect_style == "natural":
                    # 每行都有不同的微小旋转
                    angle = random.uniform(-0.5, 0.5)
                    self._draw_rotated_text(draw, line, (offset_x, offset_y), font, angle)
                else:
                    # 简单绘制
                    draw.text((offset_x, offset_y), line, font=font, fill='black')
            
            return image
        
        except Exception as e:
            logger.error(f"生成手写体图像失败: {e}")
            return None
    
    def _draw_rotated_text(self, draw, text, position, font, angle=0):
        """绘制旋转的文本
        
        Args:
            draw: ImageDraw对象
            text: 要绘制的文本
            position: 起始位置
            font: 字体
            angle: 旋转角度
        """
        # 创建一个临时图像来绘制旋转的文本
        text_width, text_height = draw.textsize(text, font=font)
        
        # 创建一个足够大的临时图像
        temp_img = Image.new('RGBA', (text_width + 20, text_height + 20), color=(255, 255, 255, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # 绘制文本到临时图像
        temp_draw.text((10, 10), text, font=font, fill='black')
        
        # 旋转临时图像
        rotated = temp_img.rotate(angle, expand=1)
        
        # 将旋转后的图像粘贴到主图像
        image_x, image_y = position
        image = draw.im
        image.paste(rotated, (int(image_x), int(image_y)), rotated)

class MockHandwritingGenerator(HandwritingGenerator):
    """模拟手写体生成器，用于测试"""
    
    def generate_handwriting(self, text: str, **kwargs) -> Optional[Image.Image]:
        """生成模拟手写体图像"""
        try:
            # 创建一个简单的图像，显示文本
            image = Image.new('RGB', (self.a5_width, self.a5_height), color='white')
            draw = ImageDraw.Draw(image)
            
            # 使用默认字体
            font = ImageFont.load_default()
            
            # 简单绘制文本
            draw.text((self.margin, self.margin), 
                     f"[模拟手写体]\n\n{text[:200]}..." if len(text) > 200 else text, 
                     font=font, 
                     fill='black')
            
            return image
        except Exception as e:
            logger.error(f"生成模拟手写体图像失败: {e}")
            return None

def get_handwriting_generator(config: Dict[str, Any], mock: bool = False) -> HandwritingGenerator:
    """获取手写体生成器实例
    
    Args:
        config: 手写体配置
        mock: 是否使用模拟生成器
        
    Returns:
        手写体生成器实例
    """
    if mock:
        return MockHandwritingGenerator(config)
    
    # 尝试使用实际的handwriting库
    try:
        # 这里可以替换为实际的handwriting库实现
        # 例如：from handwriting import SomeHandwritingGenerator
        # return SomeHandwritingGenerator(config)
        
        # 如果没有实际的handwriting库，使用Pillow实现
        logger.info("未找到实际的handwriting库，使用Pillow实现")
        return PillowHandwritingGenerator(config)
    except ImportError:
        logger.info("使用Pillow实现的手写体生成器")
        return PillowHandwritingGenerator(config)