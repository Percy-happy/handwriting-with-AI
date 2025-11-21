"""
图像导出工具模块
用于将生成的手写体图像保存为各种格式
"""
import os
import logging
from typing import Dict, Optional, List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import tempfile

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageExporter:
    """
    图像导出器类
    提供图像保存、格式转换和批量导出功能
    """
    
    def __init__(self):
        """初始化图像导出器"""
        # 支持的输出格式
        self.supported_formats = ["PNG", "JPEG", "PDF"]
        
        # 格式对应的文件扩展名
        self.format_extensions = {
            "PNG": ".png",
            "JPEG": ".jpg",
            "PDF": ".pdf"
        }
        
        # 图像质量设置
        self.quality_settings = {
            "PNG": 95,  # PNG质量（0-95）
            "JPEG": 90,  # JPEG质量（0-100）
            "PDF": 95   # PDF质量
        }
    
    def save_image(self, image: Image.Image, file_path: str, format_type: str = "PNG", 
                  quality: Optional[int] = None, optimize: bool = True) -> bool:
        """
        保存单个图像
        
        Args:
            image: PIL Image对象
            file_path: 保存路径
            format_type: 输出格式 (PNG, JPEG, PDF)
            quality: 图像质量（可选）
            optimize: 是否优化图像
            
        Returns:
            是否保存成功
        """
        try:
            # 验证格式
            if format_type.upper() not in self.supported_formats:
                logger.error(f"不支持的格式: {format_type}")
                return False
            
            # 确保文件扩展名正确
            ext = self.format_extensions[format_type.upper()]
            if not file_path.lower().endswith(ext.lower()):
                file_path += ext
            
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # 获取质量设置
            if quality is None:
                quality = self.quality_settings[format_type.upper()]
            
            # 保存图像
            if format_type.upper() == "JPEG":
                # 对于JPEG，需要确保图像模式为RGB
                if image.mode != "RGB":
                    image = image.convert("RGB")
                image.save(file_path, format="JPEG", quality=quality, optimize=optimize)
            elif format_type.upper() == "PNG":
                # PNG支持透明
                image.save(file_path, format="PNG", quality=quality, optimize=optimize)
            elif format_type.upper() == "PDF":
                # 对于PDF，确保使用RGB模式
                if image.mode != "RGB":
                    image = image.convert("RGB")
                image.save(file_path, format="PDF")
            
            logger.info(f"图像已保存到: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存图像失败: {e}")
            return False
    
    def save_images_to_pdf(self, images: List[Image.Image], file_path: str, 
                          title: Optional[str] = None) -> bool:
        """
        将多个图像保存为PDF文件
        
        Args:
            images: 图像列表
            file_path: 保存路径
            title: PDF标题（可选）
            
        Returns:
            是否保存成功
        """
        try:
            if not images:
                logger.error("没有图像可保存")
                return False
            
            # 确保文件扩展名正确
            if not file_path.lower().endswith(".pdf"):
                file_path += ".pdf"
            
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # 确保所有图像都是RGB模式
            pdf_images = []
            for img in images:
                if img.mode != "RGB":
                    pdf_images.append(img.convert("RGB"))
                else:
                    pdf_images.append(img)
            
            # 保存为PDF
            pdf_images[0].save(
                file_path,
                format="PDF",
                save_all=True,
                append_images=pdf_images[1:],
                title=title
            )
            
            logger.info(f"PDF已保存到: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存PDF失败: {e}")
            return False
    
    def batch_export(self, images: List[Tuple[Image.Image, str]], export_dir: str,
                    format_type: str = "PNG", quality: Optional[int] = None) -> Dict[str, str]:
        """
        批量导出图像
        
        Args:
            images: 图像和文件名的元组列表
            export_dir: 导出目录
            format_type: 输出格式
            quality: 图像质量
            
        Returns:
            导出结果字典 {文件名: 状态}
        """
        results = {}
        
        try:
            # 确保导出目录存在
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            
            # 批量导出
            for i, (image, base_name) in enumerate(images):
                # 生成文件名
                if not base_name:
                    base_name = f"page_{i+1}"
                
                # 构建完整路径
                ext = self.format_extensions[format_type.upper()]
                if not base_name.lower().endswith(ext.lower()):
                    base_name += ext
                
                file_path = os.path.join(export_dir, base_name)
                
                # 保存图像
                if self.save_image(image, file_path, format_type, quality):
                    results[base_name] = "success"
                else:
                    results[base_name] = "failed"
            
            return results
            
        except Exception as e:
            logger.error(f"批量导出失败: {e}")
            return {"error": str(e)}
    
    def optimize_image(self, image: Image.Image, format_type: str = "PNG") -> Image.Image:
        """
        优化图像以减小文件大小
        
        Args:
            image: PIL Image对象
            format_type: 输出格式
            
        Returns:
            优化后的图像
        """
        try:
            # 根据格式进行优化
            if format_type.upper() == "JPEG":
                # 对于JPEG，使用适度压缩
                if image.mode != "RGB":
                    image = image.convert("RGB")
                
            elif format_type.upper() == "PNG":
                # 对于PNG，尝试减少颜色数量
                if image.mode == "RGBA":
                    # 透明图像的处理
                    # 可以尝试使用有限调色板
                    pass
            
            # 应用轻微的锐化以保持清晰度
            image = image.filter(ImageFilter.SHARPEN)
            
            return image
            
        except Exception as e:
            logger.error(f"优化图像失败: {e}")
            return image  # 返回原始图像
    
    def resize_image(self, image: Image.Image, max_width: int, max_height: int, 
                    maintain_aspect_ratio: bool = True) -> Image.Image:
        """
        调整图像大小
        
        Args:
            image: PIL Image对象
            max_width: 最大宽度
            max_height: 最大高度
            maintain_aspect_ratio: 是否保持宽高比
            
        Returns:
            调整大小后的图像
        """
        try:
            if maintain_aspect_ratio:
                # 计算调整后的尺寸，保持宽高比
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            else:
                # 直接调整到指定尺寸
                image = image.resize((max_width, max_height), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            logger.error(f"调整图像大小失败: {e}")
            return image  # 返回原始图像
    
    def add_watermark(self, image: Image.Image, watermark_text: str, 
                     position: str = "bottom_right", opacity: float = 0.3) -> Image.Image:
        """
        为图像添加水印
        
        Args:
            image: PIL Image对象
            watermark_text: 水印文本
            position: 水印位置 (top_left, top_right, bottom_left, bottom_right, center)
            opacity: 水印透明度 (0.0-1.0)
            
        Returns:
            添加水印后的图像
        """
        try:
            # 创建一个副本以避免修改原始图像
            watermark_img = image.copy()
            
            # 确保图像为RGBA模式以支持透明度
            if watermark_img.mode != "RGBA":
                watermark_img = watermark_img.convert("RGBA")
            
            # 创建水印图层
            watermark_layer = Image.new("RGBA", watermark_img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(watermark_layer)
            
            # 尝试获取字体
            try:
                # 使用默认字体，设置合适的大小
                font_size = max(12, min(36, watermark_img.width // 20))
                font = ImageFont.load_default()
            except:
                # 如果无法加载字体，使用默认字体
                font = ImageFont.load_default()
            
            # 计算文本大小
            try:
                # 对于较新版本的PIL
                text_width, text_height = draw.textlength(watermark_text, font=font), font_size
            except:
                # 兼容性处理
                text_width, text_height = len(watermark_text) * 8, 16
            
            # 计算水印位置
            padding = 20
            if position == "top_left":
                x, y = padding, padding
            elif position == "top_right":
                x, y = watermark_img.width - text_width - padding, padding
            elif position == "bottom_left":
                x, y = padding, watermark_img.height - text_height - padding
            elif position == "bottom_right":
                x, y = watermark_img.width - text_width - padding, watermark_img.height - text_height - padding
            elif position == "center":
                x, y = (watermark_img.width - text_width) // 2, (watermark_img.height - text_height) // 2
            else:
                x, y = watermark_img.width - text_width - padding, watermark_img.height - text_height - padding
            
            # 绘制水印
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, int(255 * opacity)))
            
            # 合并图层
            watermark_img = Image.alpha_composite(watermark_img, watermark_layer)
            
            # 如果原始图像不是RGBA，转换回原始模式
            if image.mode != "RGBA":
                watermark_img = watermark_img.convert(image.mode)
            
            return watermark_img
            
        except Exception as e:
            logger.error(f"添加水印失败: {e}")
            return image  # 返回原始图像
    
    def export_with_settings(self, image: Image.Image, file_path: str, settings: Dict) -> bool:
        """
        根据设置导出图像
        
        Args:
            image: PIL Image对象
            file_path: 保存路径
            settings: 导出设置
            
        Returns:
            是否导出成功
        """
        try:
            # 获取设置
            format_type = settings.get("format", "PNG")
            quality = settings.get("quality")
            optimize = settings.get("optimize", True)
            add_watermark = settings.get("add_watermark", False)
            watermark_text = settings.get("watermark_text", "Handwriting AI")
            watermark_position = settings.get("watermark_position", "bottom_right")
            watermark_opacity = settings.get("watermark_opacity", 0.3)
            resize = settings.get("resize", False)
            max_width = settings.get("max_width", 2000)
            max_height = settings.get("max_height", 2000)
            maintain_aspect_ratio = settings.get("maintain_aspect_ratio", True)
            
            # 创建处理副本
            processed_image = image.copy()
            
            # 调整大小（如果需要）
            if resize:
                processed_image = self.resize_image(processed_image, max_width, max_height, maintain_aspect_ratio)
            
            # 添加水印（如果需要）
            if add_watermark:
                processed_image = self.add_watermark(processed_image, watermark_text, watermark_position, watermark_opacity)
            
            # 优化图像
            if optimize:
                processed_image = self.optimize_image(processed_image, format_type)
            
            # 保存图像
            return self.save_image(processed_image, file_path, format_type, quality, optimize)
            
        except Exception as e:
            logger.error(f"使用设置导出失败: {e}")
            return False

# 测试函数
def test_image_exporter():
    """测试图像导出器功能"""
    exporter = ImageExporter()
    
    # 创建一个测试图像
    width, height = 800, 600
    image = Image.new("RGB", (width, height), color="#f5f5f5")
    draw = ImageDraw.Draw(image)
    
    # 绘制一些测试内容
    try:
        font = ImageFont.load_default()
        draw.text((width//4, height//2), "测试图像", font=font, fill=(0, 0, 0))
    except Exception as e:
        logger.error(f"绘制测试内容失败: {e}")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"使用临时目录: {temp_dir}")
        
        # 测试保存为PNG
        png_path = os.path.join(temp_dir, "test.png")
        if exporter.save_image(image, png_path, "PNG"):
            print(f"PNG保存成功: {png_path}")
        
        # 测试保存为JPEG
        jpg_path = os.path.join(temp_dir, "test.jpg")
        if exporter.save_image(image, jpg_path, "JPEG", quality=85):
            print(f"JPEG保存成功: {jpg_path}")
        
        # 测试保存为PDF
        pdf_path = os.path.join(temp_dir, "test.pdf")
        if exporter.save_image(image, pdf_path, "PDF"):
            print(f"PDF保存成功: {pdf_path}")
        
        # 测试批量导出
        images_to_export = [(image, f"image_{i}") for i in range(3)]
        batch_results = exporter.batch_export(images_to_export, temp_dir, "PNG")
        print(f"批量导出结果: {batch_results}")
        
        # 测试水印功能
        watermarked_image = exporter.add_watermark(image, "测试水印", "bottom_right", 0.5)
        watermark_path = os.path.join(temp_dir, "watermarked.png")
        if exporter.save_image(watermarked_image, watermark_path):
            print(f"添加水印成功: {watermark_path}")
        
        # 测试使用设置导出
        export_settings = {
            "format": "JPEG",
            "quality": 90,
            "optimize": True,
            "add_watermark": True,
            "watermark_text": "Handwriting AI",
            "resize": True,
            "max_width": 600,
            "max_height": 450
        }
        settings_path = os.path.join(temp_dir, "settings.jpg")
        if exporter.export_with_settings(image, settings_path, export_settings):
            print(f"使用设置导出成功: {settings_path}")

if __name__ == "__main__":
    test_image_exporter()