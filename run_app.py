#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手写体转换应用主入口
提供命令行界面和图形界面的启动选项
"""

import sys
import os
import argparse

def print_banner():
    """
    打印应用横幅
    """
    banner = '''
    ==================================
    ||     文字转手写体应用 v1.0     ||
    ||  将普通文字转换为A5横版手写体 ||
    ==================================
    '''
    print(banner)

def check_dependencies():
    """
    检查必要的依赖是否已安装
    
    Returns:
        bool: 依赖是否都已安装
    """
    try:
        import handright
        from PIL import Image
        return True
    except ImportError as e:
        print(f"错误：缺少必要的依赖包: {e}")
        print("请运行以下命令安装依赖：")
        print("pip install handright pillow")
        return False

def start_cli():
    """
    启动命令行界面
    """
    try:
        # 确保能正确导入src模块
        import sys
        import os
        # 将当前目录添加到Python路径
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from src.cli import main as cli_main
        cli_main()
    except Exception as e:
        print(f"启动命令行界面失败: {e}")
        sys.exit(1)

def start_gui():
    """
    启动图形用户界面
    """
    try:
        import tkinter as tk
        # 确保能正确导入src模块
        import sys
        import os
        # 将当前目录添加到Python路径
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from src.gui import main as gui_main
        print("正在启动图形界面...")
        gui_main()
    except ImportError as e:
        print(f"错误：无法导入tkinter模块: {e}")
        print("tkinter通常是Python标准库的一部分，可能需要重新安装Python或安装tk依赖。")
        print("建议使用命令行界面替代。")
        sys.exit(1)
    except Exception as e:
        print(f"启动图形界面失败: {e}")
        sys.exit(1)

def main():
    """
    主入口函数
    """
    # 打印横幅
    print_banner()
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='手写体转换应用主入口')
    parser.add_argument('--cli', action='store_true', help='使用命令行界面')
    parser.add_argument('--gui', action='store_true', help='使用图形用户界面')
    # 只解析已知的参数，保留未知参数
    args, unknown = parser.parse_known_args()
    
    # 将未知参数保存到sys.argv中，以便传递给CLI
    if unknown:
        sys.argv = [sys.argv[0]] + unknown
    else:
        sys.argv = [sys.argv[0]]
    
    # 选择启动模式
    if args.cli:
        # 启动命令行界面
        start_cli()
    elif args.gui:
        # 启动图形界面
        start_gui()
    else:
        # 默认交互选择
        print("请选择要使用的界面模式：")
        print("1. 命令行界面 (CLI)")
        print("2. 图形用户界面 (GUI)")
        
        choice = input("请输入选择 (1/2，默认1): ").strip()
        
        if choice == '2':
            start_gui()
        else:
            start_cli()

if __name__ == "__main__":
    main()
