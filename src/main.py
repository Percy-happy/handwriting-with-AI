#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手写体转换应用主程序
将文字转换为横版A5大小的手写体图片
"""

from handright import Template, handwrite
from PIL import Image, ImageFont
import os
# 尝试相对导入，如果失败则使用绝对导入
try:
    from .config import HandwritingConfig, get_preset_styles
except ImportError:
    import sys
    import os
    # 将父目录添加到Python路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.config import HandwritingConfig, get_preset_styles

def convert_text_to_handwriting(text, output_path, font_path=None, style=None, custom_config=None):
    """
    将文字转换为手写体图片
    
    Args:
        text (str): 要转换的文字内容
        output_path (str): 输出图片路径
        font_path (str, optional): 字体文件路径
        style (str, optional): 预设样式名称 (default, compact, neat, casual)
        custom_config (dict, optional): 自定义配置参数
    """
    # 获取配置
    if style and style in get_preset_styles():
        config = get_preset_styles()[style]
    else:
        config = HandwritingConfig()
    
    # 如果提供了自定义配置，更新配置
    if custom_config:
        config.update_from_dict(custom_config)
    
    # 如果提供了字体路径，使用它
    if font_path and os.path.exists(font_path):
        config.font_path = font_path
    
    # 创建字体
    if config.font_path and os.path.exists(config.font_path):
        try:
            font = ImageFont.truetype(config.font_path, size=config.font_size)
        except Exception as e:
            print(f"警告：无法加载指定字体，使用默认字体: {e}")
            # 尝试使用PIL的默认字体
            font = ImageFont.load_default()
    else:
        # 使用PIL的默认字体
        font = ImageFont.load_default()
    
    # 创建模板，使用handright库支持的基本参数
    template = Template(
        background=Image.new(mode="1", size=(config.page_width, config.page_height), color=1),  # 白色背景
        font=font,  # 使用指定字体或默认字体
        line_spacing=config.line_spacing,
        word_spacing=config.word_spacing,
        left_margin=config.left_margin,
        top_margin=config.top_margin,
        right_margin=config.right_margin,
        bottom_margin=config.bottom_margin,
        line_spacing_sigma=config.line_spacing_sigma,
        word_spacing_sigma=config.word_spacing_sigma,
        font_size_sigma=config.font_size_sigma,
    )
    
    # 生成手写体
    try:
        # handwrite返回的是一个生成器，需要转换为列表
        images = list(handwrite(text, template))
        # 保存第一张图片（通常只有一张）
        if images:
            images[0].save(output_path)
            print(f"手写体图片已保存到: {output_path}")
            return True
        else:
            print("生成手写体图片失败")
            return False
    except Exception as e:
        print(f"转换过程中出错: {e}")
        return False

if __name__ == "__main__":
    # 示例文本
    example_text = "这是一个手写体转换应用示例。\n\n这个应用可以将普通文字转换为手写风格的图片，支持A5横版页面大小。\n\n你可以输入任意文字内容，系统会自动将其转换为逼真的手写效果。"
    
    # 确保输出目录存在
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # 检查是否有字体文件
    font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "LingWaiTC-Medium.otf")
    if not os.path.exists(font_path):
        font_path = None
        print("未找到字体文件，使用默认字体")
    
    # 转换并保存 - 使用默认样式
    output_path = os.path.join(output_dir, "handwritten_example.png")
    print("使用默认样式生成手写体...")
    convert_text_to_handwriting(example_text, output_path, font_path)
    
    # 示例：使用其他预设样式
    try:
        output_path_neat = os.path.join(output_dir, "handwritten_example_neat.png")
        print("使用整洁样式生成手写体...")
        convert_text_to_handwriting(example_text, output_path_neat, font_path, style="neat")
        
        output_path_casual = os.path.join(output_dir, "handwritten_example_casual.png")
        print("使用随意样式生成手写体...")
        convert_text_to_handwriting(example_text, output_path_casual, font_path, style="casual")
    except Exception as e:
        print(f"生成其他样式示例时出错: {e}")
