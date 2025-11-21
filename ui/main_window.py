"""
主窗口模块
实现应用程序的主界面
"""
import sys
import logging

# 配置日志
logger = logging.getLogger(__name__)
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
    QPushButton, QLabel, QTextEdit, QScrollArea, QSplitter,
    QMessageBox, QFileDialog
)
from PyQt6.QtGui import QPixmap, QImage, QFont, QIcon
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal
import numpy as np
from PIL import Image

# 导入自定义模块
from ui.handwriting_settings_dialog import HandwritingSettingsDialog
from ui.ai_settings_dialog import AISettingsDialog
from utils.text_processor import TextProcessor
from utils.image_exporter import ImageExporter
from config import ConfigManager
from ai_module.ai_client import get_ai_client, AIClient

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageDisplayWidget(QWidget):
    """图像显示组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.label = QLabel("暂无预览图像")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: #aaa; background-color: #333; border-radius: 5px;")
        self.label.setMinimumSize(400, 300)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.label)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: #444; border: none;")
        
        self.layout.addWidget(scroll_area)
        self.setLayout(self.layout)
    
    def set_image(self, image):
        """设置要显示的图像
        
        Args:
            image: PIL Image 对象或 QPixmap
        """
        try:
            if isinstance(image, Image.Image):
                # 转换 PIL Image 到 QPixmap
                rgb_image = image.convert('RGB')
                width, height = rgb_image.size
                data = rgb_image.tobytes()
                qimage = QImage(data, width, height, 3 * width, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qimage)
            elif isinstance(image, QPixmap):
                pixmap = image
            else:
                logger.error("无效的图像类型")
                return
            
            # 调整图像大小以适应显示区域，保持比例
            scaled_pixmap = pixmap.scaled(
                self.label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.label.setPixmap(scaled_pixmap)
        except Exception as e:
            logger.error(f"设置图像失败: {e}")
    
    def resizeEvent(self, event):
        """窗口大小改变时重新调整图像大小"""
        if hasattr(self.label, 'pixmap') and self.label.pixmap() is not None:
            self.set_image(self.label.pixmap())
        super().resizeEvent(event)

class WorkerThread(QThread):
    """工作线程，用于处理耗时操作"""
    
    finished = pyqtSignal(object)  # 完成信号，传递结果
    error = pyqtSignal(str)        # 错误信号，传递错误信息
    
    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """线程运行函数"""
        try:
            result = self.function(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    """应用程序主窗口"""
    
    def __init__(self, app_context=None):
        super().__init__()
        self.app_context = app_context
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 初始化工具类
        self.text_processor = TextProcessor()
        self.image_exporter = ImageExporter()
        self.ai_client = None
        self._initialize_ai_client()
        
        # 当前生成的手写体图像
        self.current_handwriting_image = None
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle("AI手写体生成应用")
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置深色主题
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #222;
                color: #eee;
            }
            QPushButton {
                background-color: #444;
                color: #eee;
                border: 1px solid #666;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QPushButton:pressed {
                background-color: #666;
            }
            QTextEdit, QPlainTextEdit {
                background-color: #333;
                color: #eee;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
            }
            QScrollArea, QScrollBar {
                background-color: #444;
                color: #eee;
            }
            QTabWidget::pane {
                background-color: #333;
                border: 1px solid #555;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #444;
                color: #eee;
                padding: 8px 16px;
                border: 1px solid #555;
                border-bottom: none;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #333;
                border-color: #555;
                border-bottom-color: #333;
            }
            QSplitter::handle {
                background-color: #555;
            }
            QSplitter::handle:hover {
                background-color: #666;
            }
        """)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建顶部工具栏
        toolbar_layout = QHBoxLayout()
        
        # AI设置按钮
        self.btn_ai_settings = QPushButton("AI设置")
        toolbar_layout.addWidget(self.btn_ai_settings)
        
        # 手写设置按钮
        self.btn_handwriting_settings = QPushButton("手写设置")
        toolbar_layout.addWidget(self.btn_handwriting_settings)
        
        # 模板选择下拉菜单占位
        self.btn_template = QPushButton("选择模板")
        toolbar_layout.addWidget(self.btn_template)
        
        # 添加分隔符
        toolbar_layout.addStretch()
        
        # 生成按钮
        self.btn_generate = QPushButton("生成内容")
        self.btn_generate.setStyleSheet("background-color: #4a7c59; font-weight: bold;")
        toolbar_layout.addWidget(self.btn_generate)
        
        # 转换按钮
        self.btn_convert = QPushButton("转换为手写体")
        self.btn_convert.setStyleSheet("background-color: #5c6bc0; font-weight: bold;")
        toolbar_layout.addWidget(self.btn_convert)
        
        # 导出按钮
        self.btn_export = QPushButton("导出")
        toolbar_layout.addWidget(self.btn_export)
        
        main_layout.addLayout(toolbar_layout)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 创建左侧面板（输入和编辑）
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # AI提示输入选项卡
        prompt_tab = QWidget()
        prompt_layout = QVBoxLayout(prompt_tab)
        
        self.label_prompt = QLabel("AI提示：")
        prompt_layout.addWidget(self.label_prompt)
        
        self.text_prompt = QTextEdit()
        self.text_prompt.setPlaceholderText("请输入AI提示词或使用模板...")
        prompt_layout.addWidget(self.text_prompt, 1)
        
        # 模板快捷按钮
        template_buttons_layout = QHBoxLayout()
        template_buttons = ["测试笔记", "工作汇报", "会议记录", "读书笔记", "日记模板"]
        for btn_text in template_buttons:
            btn = QPushButton(btn_text)
            btn.setFixedHeight(30)
            btn.clicked.connect(lambda checked, text=btn_text: self.on_template_clicked(text))
            template_buttons_layout.addWidget(btn)
        template_buttons_layout.addStretch()
        prompt_layout.addLayout(template_buttons_layout)
        
        prompt_tab.setLayout(prompt_layout)
        
        # 内容编辑选项卡
        content_tab = QWidget()
        content_layout = QVBoxLayout(content_tab)
        
        self.label_content = QLabel("内容编辑：")
        content_layout.addWidget(self.label_content)
        
        self.text_content = QTextEdit()
        self.text_content.setPlaceholderText("AI生成的内容将显示在这里，可以进行编辑...")
        content_layout.addWidget(self.text_content, 1)
        
        content_tab.setLayout(content_layout)
        
        # 添加选项卡到选项卡部件
        self.tab_widget.addTab(prompt_tab, "AI提示")
        self.tab_widget.addTab(content_tab, "内容编辑")
        
        left_layout.addWidget(self.tab_widget)
        
        # 创建右侧面板（预览）
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.label_preview = QLabel("预览结果：")
        right_layout.addWidget(self.label_preview)
        
        self.image_display = ImageDisplayWidget()
        right_layout.addWidget(self.image_display, 1)
        
        # 添加左右面板到分割器
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # 设置初始分割比例
        splitter.setSizes([500, 700])
        
        main_layout.addWidget(splitter, 1)
        
        # 创建状态栏
        self.statusBar().showMessage("就绪")
    
    def setup_connections(self):
        """设置信号和槽的连接"""
        self.btn_generate.clicked.connect(self.on_generate_clicked)
        self.btn_convert.clicked.connect(self.on_convert_clicked)
        self.btn_export.clicked.connect(self.on_export_clicked)
        self.btn_ai_settings.clicked.connect(self.on_ai_settings_clicked)
        self.btn_handwriting_settings.clicked.connect(self.on_handwriting_settings_clicked)
    
    def on_template_clicked(self, template_name):
        """处理模板按钮点击事件"""
        self.statusBar().showMessage(f"已选择模板：{template_name}")
        
        # 这里应该调用AI模块的模板功能
        # 暂时只是一个占位符
        self.text_prompt.setText(f"[模板：{template_name}]")
    
    def on_generate_clicked(self):
        """处理生成按钮点击事件"""
        prompt = self.text_prompt.toPlainText()
        if not prompt.strip():
            QMessageBox.warning(self, "警告", "请输入AI提示词")
            return
        
        # 检查AI客户端是否已初始化
        if not self.ai_client:
            self._initialize_ai_client()
            if not self.ai_client:
                QMessageBox.warning(self, "警告", "AI客户端未初始化，请检查AI设置")
                return
        
        self.statusBar().showMessage("正在生成内容...")
        self.set_buttons_enabled(False)
        
        # 使用工作线程执行生成任务
        def generate_task():
            try:
                # 获取AI配置
                ai_config = self.config_manager.get_ai_config()
                
                # 调用AI客户端生成内容
                content = self.ai_client.generate_content(
                    prompt,
                    temperature=ai_config.get("temperature", 0.7),
                    max_tokens=ai_config.get("max_tokens", 1000)
                )
                
                if content:
                    # 使用文本处理器对生成的内容进行格式化
                    formatted_content = self.text_processor.format_text(content)
                    return formatted_content
                else:
                    raise Exception("AI生成内容失败")
            except Exception as e:
                logger.error(f"生成内容时出错: {str(e)}")
                raise
        
        self.worker = WorkerThread(generate_task)
        self.worker.finished.connect(self.on_generate_finished)
        self.worker.error.connect(self.on_worker_error)
        self.worker.start()
    
    def on_generate_finished(self, content):
        """生成任务完成后的处理"""
        self.text_content.setPlainText(content)
        self.statusBar().showMessage("内容生成完成")
        self.set_buttons_enabled(True)
    
    def on_convert_clicked(self):
        """处理转换为手写体按钮点击事件"""
        content = self.text_content.toPlainText()
        
        if not content.strip():
            QMessageBox.warning(self, "警告", "没有内容可转换")
            return
        
        self.statusBar().showMessage("正在转换为手写体...")
        self.set_buttons_enabled(False)
        
        # 获取当前手写设置
        handwriting_config = self.config_manager.get_handwriting_config()
        
        # 使用工作线程执行转换任务
        def convert_task():
            # 这里应该调用手写体转换模块
            # 暂时返回一个模拟的图像，但使用配置中的设置
            from PIL import Image, ImageDraw, ImageFont
            import random
            
            # 使用配置中的页面大小（A5横向）
            width, height = 148*3, 210*3  # 简化的A5尺寸（毫米转像素，3像素/毫米）
            
            # 设置背景色
            background_color = handwriting_config.get('paper_color', '#ffffff')
            if background_color.startswith('#'):
                # 转换十六进制颜色为RGB
                r = int(background_color[1:3], 16)
                g = int(background_color[3:5], 16)
                b = int(background_color[5:7], 16)
                bg_color = (r, g, b)
            else:
                bg_color = 'white'
            
            img = Image.new('RGB', (width, height), color=bg_color)
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            # 获取字体大小配置
            font_size = handwriting_config.get('font_size', 12)
            line_spacing = handwriting_config.get('line_spacing', 1.5)
            margin = handwriting_config.get('margin', 20)
            
            # 使用文本处理器处理文本
            processed_text = self.text_processor.process_for_handwriting(content, font_size)
            
            # 绘制模拟手写体文本
            y = margin
            for line in processed_text.split('\n'):
                if line and y < height - margin:
                    # 添加一些随机偏移（根据手写效果配置）
                    random_offset = handwriting_config.get('random_offset', 2)
                    x = margin + random.randint(-random_offset, random_offset)
                    y += random.randint(-random_offset, random_offset)
                    
                    # 获取文字颜色
                    text_color = handwriting_config.get('text_color', '#000000')
                    if text_color.startswith('#'):
                        r = int(text_color[1:3], 16)
                        g = int(text_color[3:5], 16)
                        b = int(text_color[5:7], 16)
                        fill_color = (r, g, b)
                    else:
                        fill_color = 'black'
                    
                    draw.text((x, y), line, fill=fill_color, font=font)
                    y += int(font_size * line_spacing)
            
            return img
        
        self.worker = WorkerThread(convert_task)
        self.worker.finished.connect(self.on_convert_finished)
        self.worker.error.connect(self.on_worker_error)
        self.worker.start()
    
    def on_convert_finished(self, image):
        """转换任务完成后的处理"""
        self.current_handwriting_image = image
        self.image_display.set_image(image)
        self.statusBar().showMessage("手写体转换完成")
        self.set_buttons_enabled(True)
    
    def on_export_clicked(self):
        """处理导出按钮点击事件"""
        if not self.current_handwriting_image:
            QMessageBox.warning(self, "警告", "没有可导出的图像")
            return
        
        # 获取导出配置
        export_config = self.config_manager.get_export_config()
        default_format = export_config.get('format', 'png')
        
        # 打开文件对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "导出图像", 
            "handwriting_output." + default_format, 
            "图像文件 (*.png *.jpg *.jpeg *.pdf)"
        )
        
        if file_path:
            try:
                self.statusBar().showMessage("正在导出图像...")
                self.set_buttons_enabled(False)
                
                # 使用工作线程执行导出任务
                def export_task():
                    # 确定导出格式
                    if file_path.lower().endswith('.pdf'):
                        format_type = 'pdf'
                    elif file_path.lower().endswith(('.jpg', '.jpeg')):
                        format_type = 'jpeg'
                    else:
                        format_type = 'png'
                    
                    # 使用图像导出器
                    self.image_exporter.save_image(
                        self.current_handwriting_image, 
                        file_path, 
                        format_type=format_type,
                        quality=export_config.get('quality', 95)
                    )
                    return file_path
                
                self.worker = WorkerThread(export_task)
                self.worker.finished.connect(self.on_export_finished)
                self.worker.error.connect(self.on_worker_error)
                self.worker.start()
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败：{str(e)}")
                self.statusBar().showMessage("导出失败")
                self.set_buttons_enabled(True)
    
    def on_ai_settings_clicked(self):
        """处理AI设置按钮点击事件"""
        # 这里应该打开AI设置对话框
        # 暂时只是一个占位符
        QMessageBox.information(self, "提示", "AI设置功能正在开发中")
    
    def on_handwriting_settings_clicked(self):
        """处理手写设置按钮点击事件"""
        # 获取当前配置
        current_config = self.config_manager.get_handwriting_config()
        
        # 创建并显示手写设置对话框
        dialog = HandwritingSettingsDialog(self, current_config)
        if dialog.exec():
            # 如果用户点击了确定，保存新的配置
            new_config = dialog.get_settings()
            self.config_manager.set_handwriting_config(new_config)
            self.statusBar().showMessage("手写设置已更新")
    
    def on_export_finished(self, file_path):
        """导出任务完成后的处理"""
        QMessageBox.information(self, "成功", f"图像已成功导出到：{file_path}")
        self.statusBar().showMessage("导出完成")
        self.set_buttons_enabled(True)
    
    def on_ai_settings_clicked(self):
        """处理AI设置按钮点击事件"""
        # 创建并显示AI设置对话框
        dialog = AISettingsDialog(self, self.config_manager)
        if dialog.exec():
            # 如果用户点击了确定，设置已保存
            self.statusBar().showMessage("AI设置已更新")
            logger.info("AI设置已更新")
    
    def on_worker_error(self, error_msg):
        """处理工作线程错误"""
        QMessageBox.critical(self, "错误", f"操作失败：{error_msg}")
        self.statusBar().showMessage("操作失败")
        self.set_buttons_enabled(True)
    
    def _initialize_ai_client(self):
        """初始化AI客户端"""
        try:
            ai_config = self.config_manager.get_ai_config()
            if ai_config and "api_key" in ai_config:
                self.ai_client = get_ai_client(ai_config)
                logger.info("AI客户端初始化成功")
            else:
                logger.warning("AI配置不完整，无法初始化AI客户端")
        except Exception as e:
            logger.error(f"初始化AI客户端失败: {str(e)}")
    
    def set_buttons_enabled(self, enabled):
        """设置按钮是否可用"""
        self.btn_generate.setEnabled(enabled)
        self.btn_convert.setEnabled(enabled)
        self.btn_export.setEnabled(enabled)
        self.btn_ai_settings.setEnabled(enabled)
        self.btn_handwriting_settings.setEnabled(enabled)