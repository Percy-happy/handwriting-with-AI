#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手写体转换应用命令行界面
提供交互式文字输入和转换功能
"""

import argparse
import os
import sys
from datetime import datetime
# 尝试相对导入，如果失败则使用绝对导入
try:
    from .main import convert_text_to_handwriting
    from .config import get_preset_styles
except ImportError:
    import sys
    import os
    # 将父目录添加到Python路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.main import convert_text_to_handwriting
    from src.config import get_preset_styles

def parse_arguments():
    """
    解析命令行参数
    """
    # 获取可用的预设样式
    available_styles = list(get_preset_styles().keys())
    
    parser = argparse.ArgumentParser(description='文字转手写体应用')
    parser.add_argument('--text', '-t', type=str, help='要转换的文字内容')
    parser.add_argument('--file', '-f', type=str, help='包含要转换文字的文本文件路径')
    parser.add_argument('--output', '-o', type=str, help='输出图片路径，默认为当前时间戳命名的文件')
    parser.add_argument('--font', '-F', type=str, help='自定义字体文件路径')
    parser.add_argument('--style', '-s', type=str, choices=available_styles, default='default',
                        help=f'预设样式（默认: default），可选: {', '.join(available_styles)}')
    parser.add_argument('--interactive', '-i', action='store_true', help='启动交互式模式')
    return parser.parse_args()

def get_text_from_file(file_path):
    """
    从文件中读取文字内容
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None

def get_text_interactive():
    """
    交互式获取文字输入
    """
    print("请输入要转换的文字内容（输入空行结束输入）：")
    lines = []
    while True:
        try:
            line = input()
            if not line:  # 空行表示结束输入
                break
            lines.append(line)
        except EOFError:
            break
    return '\n'.join(lines)

def get_style_interactive():
    """
    交互式获取样式选择
    """
    available_styles = list(get_preset_styles().keys())
    print(f"请选择手写体样式（默认: default）")
    print("可用样式：")
    style_descriptions = {
        'default': '默认样式，平衡的手写效果',
        'compact': '紧凑样式，节省空间',
        'neat': '整洁样式，更加规整',
        'casual': '随意样式，更加自然'}
    
    for style in available_styles:
        desc = style_descriptions.get(style, '')
        print(f"  - {style}: {desc}")
    
    style_input = input("请输入样式名称（直接回车使用默认样式）: ").strip()
    if not style_input or style_input not in available_styles:
        return 'default'
    return style_input

def generate_output_path(base_output=None):
    """
    生成输出文件路径
    """
    if base_output:
        return base_output
    
    # 默认输出目录
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # 使用时间戳生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(output_dir, f"handwritten_{timestamp}.png")

def main():
    """
    命令行界面主函数
    """
    args = parse_arguments()
    text = None
    
    # 获取文字内容
    if args.text:
        text = args.text
    elif args.file:
        text = get_text_from_file(args.file)
    elif args.interactive:
        text = get_text_interactive()
        # 在交互式模式下，允许用户选择样式
        args.style = get_style_interactive()
    else:
        # 如果没有指定任何输入方式，默认启动交互式模式
        text = get_text_interactive()
        args.style = get_style_interactive()
    
    if not text:
        print("错误：没有提供要转换的文字内容")
        print("请使用 -t 指定文字，或 -f 指定文本文件，或使用 -i 进入交互式模式")
        sys.exit(1)
    
    # 生成输出路径
    output_path = generate_output_path(args.output)
    
    # 转换文字
    print(f"正在转换文字为手写体...")
    print(f"使用样式: {args.style}")
    success = convert_text_to_handwriting(text, output_path, args.font, style=args.style)
    
    if success:
        print(f"转换成功！手写体图片已保存到: {output_path}")
    else:
        print("转换失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()
