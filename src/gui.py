#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手写体转换应用图形用户界面
提供可视化的文字输入、Ollama AI交互和转换功能
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import threading
import asyncio
import socket  # 移到外部导入
from PIL import Image, ImageTk
# 尝试相对导入，如果失败则使用绝对导入
try:
    from .main import convert_text_to_handwriting
    from .config import get_preset_styles
    from .ollama_utils import (
        get_ollama_models, stream_chat_with_ollama,
        DEFAULT_SYSTEM_PROMPT, TEXT_ENHANCEMENT_PROMPT
    )
except ImportError:
    import sys
    import os
    # 将父目录添加到Python路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.main import convert_text_to_handwriting
    from src.config import get_preset_styles
    from src.ollama_utils import (
        get_ollama_models, stream_chat_with_ollama,
        DEFAULT_SYSTEM_PROMPT, TEXT_ENHANCEMENT_PROMPT
    )

class HandwritingApp:
    """
    手写体转换应用GUI类
    集成Ollama AI功能
    """
    def __init__(self, root):
        """
        初始化GUI应用
        
        Args:
            root: tkinter根窗口
        """
        self.root = root
        self.root.title("AI辅助手写体转换应用")
        self.root.geometry("900x700")
        
        # Ollama相关属性
        self.selected_model = tk.StringVar(value="")
        self.ai_response = ""
        self.stream_running = False
        
        # 创建标签页控件
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建主转换页面
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="文字转手写体")
        
        # 创建AI交互页面
        self.ai_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ai_frame, text="AI辅助编辑")
        
        # 设置主页面UI
        self.setup_main_ui()
        
        # 设置AI页面UI
        self.setup_ai_ui()
        
        # 底部状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_main_ui(self):
        """
        设置主转换页面UI组件
        """
        # 创建主框架
        main_frame = self.main_frame
        
        # 文字输入区域
        ttk.Label(main_frame, text="输入要转换的文字：").pack(anchor=tk.W, pady=(10, 5))
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
        
        # 从AI页面导入按钮
        ttk.Button(control_frame, text="从AI导入内容", command=self.import_from_ai).pack(side=tk.RIGHT, padx=(10, 0))
        
        # 转换按钮
        ttk.Button(control_frame, text="转换为手写体", command=self.convert_text).pack(side=tk.RIGHT)
        
        # 预览区域
        ttk.Label(main_frame, text="预览：").pack(anchor=tk.W, pady=(10, 5))
        self.preview_frame = ttk.Frame(main_frame, relief=tk.SUNKEN)
        self.preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # 预览标签
        self.preview_label = ttk.Label(self.preview_frame, text="转换后的手写体图片将在这里显示")
        self.preview_label.pack(expand=True)
    
    def setup_ai_ui(self):
        """
        设置AI辅助编辑页面UI组件
        """
        ai_frame = self.ai_frame
        
        # 顶部提示
        ttk.Label(ai_frame, text="使用AI助手帮助您编辑和优化文本内容").pack(anchor=tk.W, pady=(10, 5))
        
        # 模型选择区域
        model_frame = ttk.Frame(ai_frame)
        model_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(model_frame, text="选择Ollama模型：").pack(side=tk.LEFT, padx=(0, 5))
        
        # 刷新模型按钮
        ttk.Button(model_frame, text="刷新模型列表", command=self.refresh_ollama_models).pack(side=tk.RIGHT, padx=(10, 0))
        
        # 模型下拉框
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.selected_model, state="readonly", width=30)
        self.model_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # 刷新模型列表
        self.refresh_ollama_models()
        
        # 提示词输入区域
        prompt_frame = ttk.Frame(ai_frame)
        prompt_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(prompt_frame, text="输入您的需求：").pack(anchor=tk.W, pady=(5, 5))
        self.prompt_input = scrolledtext.ScrolledText(prompt_frame, wrap=tk.WORD, height=5, width=80)
        self.prompt_input.pack(fill=tk.X, pady=(0, 5))
        self.prompt_input.insert(tk.END, "请帮我生成一段关于Python编程学习的内容，适合手写练习。")
        
        # 预设提示词按钮
        preset_frame = ttk.Frame(prompt_frame)
        preset_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(preset_frame, text="生成文本", command=lambda: self.prompt_input.insert(tk.END, "请帮我生成一段关于...的内容，适合手写练习。")).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(preset_frame, text="优化文本", command=lambda: self.prompt_input.insert(tk.END, "请帮我优化以下文本使其更适合手写：")).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(preset_frame, text="调整格式", command=lambda: self.prompt_input.insert(tk.END, "请帮我调整以下文本的格式，使其更易读：")).pack(side=tk.LEFT)
        
        # 控制按钮
        control_frame = ttk.Frame(ai_frame)
        control_frame.pack(fill=tk.X, pady=(10, 10))
        
        self.send_button = ttk.Button(control_frame, text="发送请求", command=self.send_ai_request)
        self.send_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="停止生成", command=self.stop_ai_generation, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="清空输出", command=self.clear_ai_output).pack(side=tk.RIGHT, padx=(10, 0))
        
        # AI响应显示区域
        ttk.Label(ai_frame, text="AI响应：").pack(anchor=tk.W, pady=(5, 5))
        self.ai_output = scrolledtext.ScrolledText(ai_frame, wrap=tk.WORD, height=15, width=80)
        self.ai_output.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 底部导入按钮
        bottom_frame = ttk.Frame(ai_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(bottom_frame, text="导入到转换页", command=self.import_to_main).pack(side=tk.RIGHT)
    
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
    
    def show_error_dialog(self, title, message):
        """
        显示错误对话框
        
        Args:
            title: 对话框标题
            message: 错误消息
        """
        messagebox.showerror(title, message)
        
    def show_info_dialog(self, title, message):
        """
        显示信息对话框
        
        Args:
            title: 对话框标题
            message: 信息消息
        """
        messagebox.showinfo(title, message)
    
    def refresh_ollama_models(self):
        """
        刷新Ollama可用模型列表
        """
        try:
            if not hasattr(self, 'status_var'):
                self.status_var = tk.StringVar(value="正在获取Ollama模型列表...")
            else:
                self.status_var.set("正在获取Ollama模型列表...")
                
            # 设置超时时间，避免长时间等待
            socket.setdefaulttimeout(10)  # 设置10秒超时
            
            # 显示进度信息
            self.show_info_dialog("提示", "正在连接Ollama服务获取可用模型...\n请稍候片刻...")
            
            # get_ollama_models() 现在直接返回模型名称列表
            model_names = get_ollama_models()
            
            if model_names:
                self.model_combo['values'] = model_names
                if model_names:
                    # 默认选择第一个模型
                    self.selected_model.set(model_names[0])
                
                # 格式化模型列表，方便用户查看
                models_text = "\n".join([f"- {model}" for model in model_names])
                self.status_var.set(f"已加载 {len(model_names)} 个模型")
                self.show_info_dialog(
                    "成功", 
                    f"已成功加载 {len(model_names)} 个Ollama模型\n\n{models_text}\n\n现在您可以开始使用AI功能了！"
                )
            else:
                self.model_combo['values'] = []
                self.selected_model.set("")
                self.status_var.set("未找到可用的Ollama模型")
                
                # 详细的错误提示和故障排除步骤
                self.show_error_dialog(
                    "模型未找到", 
                    "未找到可用的Ollama模型，请按照以下步骤检查：\n\n"+
                    "1. 确保Ollama服务已启动（打开Ollama应用或执行'ollama serve'）\n"+
                    "2. 确认Ollama服务正在监听11434端口\n"+
                    "3. 打开Ollama应用或命令行下载至少一个模型：\n"+
                    "   - 例如：'ollama pull qwen3:0.5b'\n"+
                    "4. 下载完成后再次点击刷新模型按钮"
                )
                
                # 提供一个测试按钮来检查Ollama服务状态
                self.test_ollama_service()
                
        except socket.timeout:
            self.status_var.set("连接超时")
            self.show_error_dialog(
                "连接超时", 
                "无法连接到Ollama服务，请执行以下检查：\n\n"+
                "1. Ollama服务是否正在运行？\n"+
                "2. 网络连接是否正常？\n"+
                "3. 防火墙是否阻止了连接？\n"+
                "4. 尝试重启Ollama服务后再次刷新模型"
            )
            
        except ConnectionRefusedError:
            self.status_var.set("连接被拒绝")
            self.show_error_dialog(
                "连接失败", 
                "Ollama服务连接被拒绝：\n\n"+
                "1. 确认Ollama服务正在运行\n"+
                "2. 检查服务地址是否为http://localhost:11434\n"+
                "3. 如果服务在不同地址，请修改配置文件中的Ollama地址\n"+
                "4. 尝试重启Ollama应用程序"
            )
            
        except Exception as e:
            self.status_var.set(f"获取模型失败")
            self.show_error_dialog(
                "错误", 
                f"获取Ollama模型列表失败: {str(e)}\n\n"+
                "可能的原因：\n"+
                "1. Ollama服务未运行或崩溃\n"+
                "2. Python ollama库安装问题\n"+
                "3. 权限不足无法访问服务\n\n"+
                "请尝试重启Ollama服务和应用程序"
            )
            
    def test_ollama_service(self):
        """
        测试Ollama服务是否正在运行并可访问
        """
        try:
            # 创建一个简单的测试对话框
            test_window = tk.Toplevel(self.root)
            test_window.title("Ollama服务测试")
            test_window.geometry("400x300")
            test_window.resizable(False, False)
            
            # 居中显示
            test_window.transient(self.root)
            test_window.grab_set()
            
            # 添加测试结果文本框
            result_text = tk.Text(test_window, wrap=tk.WORD, width=45, height=12)
            result_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
            
            # 添加关闭按钮
            close_button = tk.Button(test_window, text="关闭", command=test_window.destroy, 
                                   width=15, height=1, font=('SimHei', 10))
            close_button.pack(pady=10)
            
            # 测试服务连接
            result_text.insert(tk.END, "正在测试Ollama服务连接...\n")
            
            # 在单独线程中执行测试以避免UI冻结
            def run_test():
                try:
                    import requests
                    
                    # 直接测试API端点
                    url = "http://localhost:11434/"
                    response = requests.get(url, timeout=3)
                    test_result = f"✓ 服务响应状态码: {response.status_code}\n"
                    
                    # 测试模型列表API
                    models_url = "http://localhost:11434/api/tags"
                    models_response = requests.get(models_url, timeout=3)
                    
                    if models_response.status_code == 200:
                        data = models_response.json()
                        if 'models' in data and isinstance(data['models'], list):
                            test_result += f"✓ 模型列表API正常，发现 {len(data['models'])} 个模型\n"
                        else:
                            test_result += "! 模型列表API响应格式异常\n"
                    else:
                        test_result += f"! 模型列表API错误: {models_response.status_code}\n"
                    
                    # 检查进程
                    import subprocess
                    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                    ollama_processes = [line for line in result.stdout.split('\n') if 'ollama' in line]
                    test_result += f"\n找到 {len(ollama_processes)} 个Ollama相关进程\n"
                    
                except requests.exceptions.ConnectionError:
                    test_result = "✗ 无法连接到Ollama服务，请确保服务正在运行\n"
                except requests.exceptions.Timeout:
                    test_result = "✗ 连接Ollama服务超时\n"
                except Exception as e:
                    test_result = f"✗ 测试过程中出错: {e}\n"
                
                # 在主线程中更新UI
                def update_ui():
                    result_text.insert(tk.END, test_result)
                    result_text.insert(tk.END, "\n提示：如果测试失败，请重启Ollama应用并下载模型")
                    result_text.config(state=tk.DISABLED)  # 设置为只读
                
                self.root.after(0, update_ui)
            
            # 启动测试线程
            import threading
            test_thread = threading.Thread(target=run_test)
            test_thread.daemon = True
            test_thread.start()
            
        except Exception as e:
            self.show_error_dialog("测试失败", f"执行Ollama服务测试时出错: {e}")
    
    def send_ai_request(self):
        """
        发送AI请求并处理流式响应
        """
        # 确保status_var存在
        if not hasattr(self, 'status_var'):
            self.status_var = tk.StringVar(value="就绪")
            
        prompt = self.prompt_input.get(1.0, tk.END).strip()
        if not prompt:
            self.status_var.set("请输入提示词")
            self.show_error_dialog("提示", "请输入提示词后再发送请求")
            return
        
        model = self.selected_model.get()
        if not model:
            self.status_var.set("请选择Ollama模型")
            self.show_error_dialog("提示", "请先选择一个Ollama模型")
            return
        
        try:
            # 清空之前的输出
            self.ai_output.delete(1.0, tk.END)
            self.ai_response = ""
            
            # 更新状态
            self.status_var.set(f"正在请求模型 {model}...")
            
            # 禁用发送按钮，启用停止按钮
            self.send_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # 创建停止标志
            self.stop_generation = False
            
            # 在单独线程中运行流式响应
            def run_stream():
                try:
                    # 构建系统提示
                    system_prompt = {
                        "role": "system",
                        "content": "你是一个专业的文本编辑助手，擅长帮助用户创建和优化适合手写的文本内容。请确保输出格式清晰，段落分明，易于阅读和手写。"
                    }
                    
                    # 构建用户消息
                    user_message = {
                        "role": "user",
                        "content": prompt
                    }
                    
                    # 设置超时
                    socket.setdefaulttimeout(30)  # 30秒超时
                    
                    # 流式获取响应，直接传入prompt字符串
                    success = False
                    # 从system_prompt字典中提取content作为系统提示词
                    system_prompt_text = system_prompt['content']
                    for content in stream_chat_with_ollama(model, prompt, system_prompt_text):
                        if self.stop_generation:
                            break
                        success = True
                            
                        # 在主线程中更新UI
                        def update_ui(content=content):
                            self.ai_output.insert(tk.END, content)
                            self.ai_output.see(tk.END)
                            self.ai_response += content
                            
                        self.root.after(0, update_ui)
                    
                    # 完成后的操作
                    if not success and not self.stop_generation:
                        self.root.after(0, lambda: self.status_var.set("未收到AI响应"))
                        self.root.after(0, lambda: self.show_error_dialog("无响应", "未收到AI模型的响应，请检查模型是否正常工作"))
                    elif not self.stop_generation:
                        self.root.after(0, lambda: self.status_var.set("AI生成完成"))
                        # 移除对不存在的import_button的引用
                except socket.timeout:
                    self.root.after(0, lambda: self.status_var.set("AI请求超时"))
                    self.root.after(0, lambda: self.show_error_dialog("请求超时", "AI模型响应超时，请尝试更简单的提示或检查模型状态"))
                except ConnectionRefusedError:
                    self.root.after(0, lambda: self.status_var.set("连接失败"))
                    self.root.after(0, lambda: self.show_error_dialog("连接失败", "无法连接到Ollama服务，请确保服务正在运行"))
                except KeyError as e:
                    self.root.after(0, lambda: self.status_var.set("响应格式错误"))
                    self.root.after(0, lambda: self.show_error_dialog("格式错误", f"AI响应格式错误: {str(e)}"))
                except Exception as e:
                    error_msg = f"AI请求处理失败: {str(e)}"
                    self.root.after(0, lambda: self.status_var.set(f"AI请求失败"))
                    self.root.after(0, lambda msg=error_msg: self.show_error_dialog("错误", msg))
                finally:
                    # 恢复按钮状态
                    self.root.after(0, lambda: self.send_button.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
            
            # 启动线程
            thread = threading.Thread(target=run_stream)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.status_var.set(f"启动请求失败")
            self.show_error_dialog("错误", f"启动AI请求失败: {str(e)}")
            self.send_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def stop_ai_generation(self):
        """
        停止AI生成
        """
        self.stop_generation = True
        self.status_var.set("已停止AI生成")
        self.send_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def clear_ai_output(self):
        """
        清空AI输出
        """
        self.ai_output.delete(1.0, tk.END)
        self.ai_response = ""
        self.status_var.set("已清空AI输出")
    
    def import_to_main(self):
        """
        将AI生成的内容导入到主转换页面
        """
        if self.ai_response:
            # 切换到主页面
            self.notebook.select(0)
            # 清空主页面输入
            self.text_input.delete(1.0, tk.END)
            # 导入AI生成的内容
            self.text_input.insert(tk.END, self.ai_response)
            self.status_var.set("已从AI页面导入内容")
        else:
            self.status_var.set("没有可导入的AI生成内容")
    
    def import_from_ai(self):
        """
        从主页面触发导入AI内容
        """
        if self.ai_response:
            # 清空主页面输入
            self.text_input.delete(1.0, tk.END)
            # 导入AI生成的内容
            self.text_input.insert(tk.END, self.ai_response)
            self.status_var.set("已从AI页面导入内容")
        else:
            self.status_var.set("没有可导入的AI生成内容")
            # 切换到AI页面，让用户先生成内容
            self.notebook.select(1)
    
    def convert_text(self):
        """
        转换文字为手写体
        """
        # 获取输入
        text = self.text_input.get(1.0, tk.END).strip()
        if not text:
            self.show_error_dialog("警告", "请输入要转换的文字")
            return
        
        # 获取配置
        style = self.style_var.get()
        font_path = self.font_path_var.get()
        
        # 验证字体文件
        if font_path and not os.path.exists(font_path):
            self.show_error_dialog("文件不存在", f"指定的字体文件不存在: {font_path}\n将使用默认字体")
            font_path = None
        
        # 生成输出路径
        try:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
            os.makedirs(output_dir, exist_ok=True)
            
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"handwritten_gui_{timestamp}.png")
        except Exception as e:
            self.show_error_dialog("路径错误", f"无法创建输出目录或文件: {str(e)}")
            self.status_var.set("路径设置失败")
            return
        
        # 转换文字
        self.status_var.set("正在转换...")
        self.root.update()
        
        try:
            # 检查文本长度，避免处理过长的文本
            if len(text) > 10000:
                self.show_error_dialog("文本过长", "文本长度超过10000个字符，请减少文本量后重试")
                self.status_var.set("文本过长")
                return
            
            success = convert_text_to_handwriting(text, output_path, font_path, style=style)
            
            if success:
                self.status_var.set(f"转换成功！文件已保存")
                self.show_info_dialog("成功", f"转换成功！\n文件已保存到: {output_path}")
                self.show_preview(output_path)
            else:
                self.show_error_dialog("错误", "转换失败，请检查错误信息")
                self.status_var.set("转换失败")
        except MemoryError:
            self.show_error_dialog("内存不足", "处理过程中内存不足，请尝试减少文本量或关闭其他应用程序")
            self.status_var.set("内存错误")
        except PermissionError:
            self.show_error_dialog("权限错误", "没有写入权限，请检查输出目录权限设置")
            self.status_var.set("权限错误")
        except Exception as e:
            self.show_error_dialog("错误", f"转换过程中出错: {str(e)}")
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
