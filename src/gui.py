#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手写体转换应用图形用户界面
提供可视化的文字输入和转换功能
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
from PIL import Image, ImageTk
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

class HandwritingApp:
    """
    手写体转换应用GUI类
    """
    def __init__(self, root):
        """
        初始化GUI应用
        
        Args:
            root: tkinter根窗口
        """
        self.root = root
        self.root.title("文字转手写体应用")
        self.root.geometry("800x600")
        
        # 确保中文显示正常
        self.setup_ui()
        
    def setup_ui(self):
        """
        设置用户界面组件
        """
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文字输入区域
        ttk.Label(main_frame, text="输入要转换的文字：").pack(anchor=tk.W)
        self.text_input = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=10, width=80)
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 控制区域
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 样式选择
        ttk.Label(control_frame, text="选择样式：").pack(side=tk.LEFT, padx=(0, 5))
        available_styles = list(get_preset_styles().keys())
        self.style_var = tk.StringVar(value="default")
        style_combo = ttk.Combobox(control_frame, textvariable=self.style_var, values=available_styles, state="readonly", width=10)
        style_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # 字体文件选择
        self.font_path_var = tk.StringVar(value="")
        ttk.Label(control_frame, text="字体文件：").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(control_frame, textvariable=self.font_path_var, width=30).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="浏览", command=self.browse_font_file).pack(side=tk.LEFT, padx=(0, 10))
        
        # 转换按钮
        ttk.Button(control_frame, text="转换为手写体", command=self.convert_text).pack(side=tk.RIGHT)
        
        # 预览区域
        ttk.Label(main_frame, text="预览：").pack(anchor=tk.W)
        self.preview_frame = ttk.Frame(main_frame, relief=tk.SUNKEN)
        self.preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # 预览标签
        self.preview_label = ttk.Label(self.preview_frame, text="转换后的手写体图片将在这里显示")
        self.preview_label.pack(expand=True)
        
        # 底部状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def browse_font_file(self):
        """
        浏览字体文件
        """
        file_path = filedialog.askopenfilename(
            title="选择字体文件",
            filetypes=[("字体文件", "*.ttf *.otf *.ttc"), ("所有文件", "*")]
        )
        if file_path:
            self.font_path_var.set(file_path)
    
    def convert_text(self):
        """
        转换文字为手写体
        """
        # 获取输入
        text = self.text_input.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("警告", "请输入要转换的文字")
            return
        
        # 获取配置
        style = self.style_var.get()
        font_path = self.font_path_var.get()
        if not os.path.exists(font_path):
            font_path = None
        
        # 生成输出路径
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"handwritten_gui_{timestamp}.png")
        
        # 转换文字
        self.status_var.set("正在转换...")
        self.root.update()
        
        try:
            success = convert_text_to_handwriting(text, output_path, font_path, style=style)
            
            if success:
                self.status_var.set(f"转换成功！文件已保存到: {output_path}")
                self.show_preview(output_path)
            else:
                messagebox.showerror("错误", "转换失败，请检查错误信息")
                self.status_var.set("转换失败")
        except Exception as e:
            messagebox.showerror("错误", f"转换过程中出错: {str(e)}")
            self.status_var.set(f"错误: {str(e)}")
    
    def show_preview(self, image_path):
        """
        显示转换后的图片预览
        
        Args:
            image_path: 图片路径
        """
        try:
            # 加载图片
            image = Image.open(image_path)
            
            # 调整图片大小以适应预览区域
            max_width = self.preview_frame.winfo_width() - 20
            max_height = self.preview_frame.winfo_height() - 20
            
            # 如果预览区域还没有大小信息，使用默认值
            if max_width < 100:  # 假设100是最小合理宽度
                max_width = 700
            if max_height < 100:
                max_height = 400
            
            # 计算调整后的尺寸，保持宽高比
            width, height = image.size
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            # 调整图片大小
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为tkinter可用的格式
            tk_image = ImageTk.PhotoImage(resized_image)
            
            # 更新预览
            self.preview_label.config(image=tk_image, text="")
            self.preview_label.image = tk_image  # 保持引用，防止被垃圾回收
            
        except Exception as e:
            messagebox.showerror("错误", f"显示预览失败: {str(e)}")

def main():
    """
    启动GUI应用
    """
    root = tk.Tk()
    app = HandwritingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
