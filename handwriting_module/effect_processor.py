"""
手写体效果处理模块
负责增强手写体的真实感和多样性
"""
import logging
import random
from typing import Optional
from PIL import Image, ImageFilter, ImageEnhance

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EffectProcessor:
    """手写体效果处理器"""
    
    def __init__(self):
        # 效果类型配置
        self.effect_levels = {
            "none": {"enabled": False},
            "limited": {
                "enabled": True,
                "ink_spread": 0.1,
                "noise": 0.05,
                "blur": 0.5,
                "rotation": 0.5
            },
            "natural": {
                "enabled": True,
                "ink_spread": 0.3,
                "noise": 0.1,
                "blur": 1.0,
                "rotation": 1.0
            },
            "strong": {
                "enabled": True,
                "ink_spread": 0.5,
                "noise": 0.2,
                "blur": 1.5,
                "rotation": 1.5
            }
        }
    
    def apply_effects(self, image: Image.Image, effect_style: str = "limited") -> Optional[Image.Image]:
        """应用效果到图像
        
        Args:
            image: 原始图像
            effect_style: 效果风格（none, limited, natural, strong）
            
        Returns:
            处理后的图像或None
        """
        try:
            # 获取效果配置
            config = self.effect_levels.get(effect_style, self.effect_levels["limited"])
            
            if not config["enabled"]:
                return image
            
            # 创建图像副本
            processed_image = image.copy()
            
            # 应用各种效果
            processed_image = self._apply_ink_spread(processed_image, config["ink_spread"])
            processed_image = self._apply_noise(processed_image, config["noise"])
            processed_image = self._apply_blur(processed_image, config["blur"])
            processed_image = self._apply_paper_texture(processed_image)
            processed_image = self._adjust_brightness_contrast(processed_image)
            
            return processed_image
        
        except Exception as e:
            logger.error(f"应用效果失败: {e}")
            return None
    
    def _apply_ink_spread(self, image: Image.Image, intensity: float) -> Image.Image:
        """应用墨水扩散效果
        
        Args:
            image: 图像
            intensity: 强度（0-1）
            
        Returns:
            处理后的图像
        """
        if intensity <= 0:
            return image
        
        # 使用膨胀和腐蚀操作模拟墨水扩散
        # 对于RGB图像，先转为灰度
        gray = image.convert('L')
        
        # 使用PIL的滤镜效果
        # 这里使用最小滤镜模拟墨水扩散
        # 实际应用中可能需要更复杂的形态学操作
        kernel_size = max(1, int(intensity * 3))
        
        # 对黑色区域进行扩展
        # 创建蒙版
        threshold = 128
        mask = gray.point(lambda x: 255 if x < threshold else 0, '1')
        
        # 应用滤镜
        blurred = mask.filter(ImageFilter.GaussianBlur(radius=kernel_size))
        
        # 将处理后的蒙版与原图合并
        result = Image.new('RGB', image.size, color='white')
        
        # 先绘制原图
        result.paste(image, (0, 0))
        
        # 然后使用处理后的蒙版覆盖
        # 由于蒙版是白色背景黑色文字，我们需要反转它
        inverted_mask = blurred.point(lambda x: 255 - x, 'L')
        
        # 创建一个黑色图像，使用蒙版
        ink_layer = Image.new('RGB', image.size, color='black')
        ink_layer.putalpha(inverted_mask)
        
        # 使用较低的不透明度合并
        result.paste(ink_layer, (0, 0), ink_layer)
        
        return result
    
    def _apply_noise(self, image: Image.Image, intensity: float) -> Image.Image:
        """添加随机噪声
        
        Args:
            image: 图像
            intensity: 强度（0-1）
            
        Returns:
            处理后的图像
        """
        if intensity <= 0:
            return image
        
        # 转换为RGBA以支持透明度
        rgba = image.convert('RGBA')
        pixels = rgba.load()
        width, height = rgba.size
        
        # 添加噪声
        for i in range(width):
            for j in range(height):
                # 随机决定是否添加噪声点
                if random.random() < intensity:
                    # 生成随机噪声值
                    noise = random.randint(-30, 30)
                    r, g, b, a = pixels[i, j]
                    
                    # 调整颜色值
                    r = max(0, min(255, r + noise))
                    g = max(0, min(255, g + noise))
                    b = max(0, min(255, b + noise))
                    
                    pixels[i, j] = (r, g, b, a)
        
        # 转回RGB
        return rgba.convert('RGB')
    
    def _apply_blur(self, image: Image.Image, intensity: float) -> Image.Image:
        """应用模糊效果
        
        Args:
            image: 图像
            intensity: 强度（0-1）
            
        Returns:
            处理后的图像
        """
        if intensity <= 0:
            return image
        
        # 使用高斯模糊
        radius = intensity * 0.5  # 限制最大模糊半径
        return image.filter(ImageFilter.GaussianBlur(radius=radius))
    
    def _apply_paper_texture(self, image: Image.Image) -> Image.Image:
        """应用纸张纹理
        
        Args:
            image: 图像
            
        Returns:
            处理后的图像
        """
        try:
            # 创建一个简单的纸张纹理
            width, height = image.size
            paper = Image.new('RGB', (width, height), color='white')
            
            # 添加细微的颜色变化
            pixels = paper.load()
            for i in range(width):
                for j in range(height):
                    # 生成纸张颜色变化
                    paper_color = random.randint(240, 255)
                    pixels[i, j] = (paper_color, paper_color, paper_color)
            
            # 将原始图像与纸张纹理合并
            # 转换为RGBA以支持合成
            img_rgba = image.convert('RGBA')
            paper_rgba = paper.convert('RGBA')
            
            # 使用合成操作
            result = Image.blend(paper_rgba, img_rgba, 0.95)
            
            return result.convert('RGB')
        except Exception as e:
            logger.warning(f"应用纸张纹理失败: {e}，跳过此效果")
            return image
    
    def _adjust_brightness_contrast(self, image: Image.Image) -> Image.Image:
        """调整亮度和对比度
        
        Args:
            image: 图像
            
        Returns:
            处理后的图像
        """
        # 轻微降低亮度，增加真实感
        brightness = ImageEnhance.Brightness(image)
        image = brightness.enhance(0.95)
        
        # 轻微增加对比度
        contrast = ImageEnhance.Contrast(image)
        image = contrast.enhance(1.05)
        
        return image
    
    def apply_writing_variation(self, image: Image.Image) -> Optional[Image.Image]:
        """应用书写变化效果（更复杂的模拟）
        
        Args:
            image: 原始图像
            
        Returns:
            处理后的图像或None
        """
        try:
            # 创建图像副本
            result = image.copy()
            
            # 应用细微的线条粗细变化
            # 这可以通过使用不同的阈值和滤镜来实现
            gray = result.convert('L')
            
            # 使用随机阈值处理不同区域
            width, height = gray.size
            for y in range(0, height, 10):
                for x in range(0, width, 10):
                    # 随机选择阈值
                    threshold = random.randint(100, 150)
                    
                    # 对小区域应用阈值
                    for dy in range(min(10, height - y)):
                        for dx in range(min(10, width - x)):
                            if gray.getpixel((x + dx, y + dy)) < threshold:
                                # 使一些像素更暗
                                if random.random() < 0.3:
                                    result.putpixel((x + dx, y + dy), (0, 0, 0))
            
            return result
        except Exception as e:
            logger.error(f"应用书写变化效果失败: {e}")
            return None
    
    def create_handwriting_with_pen_pressure(self, image: Image.Image) -> Optional[Image.Image]:
        """模拟钢笔压力效果
        
        Args:
            image: 原始图像
            
        Returns:
            处理后的图像或None
        """
        try:
            # 转换为灰度
            gray = image.convert('L')
            
            # 创建新图像
            result = Image.new('RGB', image.size, color='white')
            draw = ImageDraw.Draw(result)
            
            # 扫描图像，根据位置调整线条粗细
            width, height = gray.size
            for y in range(height):
                for x in range(width):
                    pixel_value = gray.getpixel((x, y))
                    
                    # 如果是黑色像素（文字）
                    if pixel_value < 128:
                        # 模拟钢笔压力
                        # 行首和行尾压力较小，中间压力较大
                        line_pos = x / width
                        pressure = 1.0
                        
                        if line_pos < 0.2:
                            pressure = 0.5 + line_pos * 0.5  # 逐渐增加
                        elif line_pos > 0.8:
                            pressure = 0.5 + (1.0 - line_pos) * 0.5  # 逐渐减少
                        
                        # 随机调整压力
                        pressure *= random.uniform(0.8, 1.2)
                        
                        # 根据压力调整像素颜色
                        intensity = 255 - int((255 - pixel_value) * pressure)
                        draw.point((x, y), fill=(intensity, intensity, intensity))
            
            return result
        except Exception as e:
            logger.error(f"应用钢笔压力效果失败: {e}")
            return None

# 导入ImageDraw（在函数中需要）
from PIL import ImageDraw