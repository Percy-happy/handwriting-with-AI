"""
手写设置对话框模块
用于配置手写体样式和效果参数
"""
import sys
import logging
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QGroupBox, QSlider, QCheckBox, QGridLayout,
    QMessageBox, QFrame
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HandwritingSettingsDialog(QDialog):
    """手写设置对话框"""
    
    def __init__(self, parent=None, config_manager=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("手写设置")
        self.setMinimumSize(500, 600)
        self.setModal(True)
        
        # 设置深色主题
        self.setStyleSheet("""
            QDialog, QWidget {
                background-color: #222;
                color: #eee;
            }
            QLabel {
                color: #ddd;
            }
            QComboBox {
                background-color: #333;
                color: #eee;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton {
                background-color: #444;
                color: #eee;
                border: 1px solid #666;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QPushButton:pressed {
                background-color: #666;
            }
            QPushButton#btn_save {
                background-color: #4a7c59;
                font-weight: bold;
            }
            QPushButton#btn_save:hover {
                background-color: #5a8c69;
            }
            QGroupBox {
                background-color: #2a2a2a;
                border: 1px solid #555;
                border-radius: 6px;
                margin: 10px 0;
                padding: 10px;
            }
            QGroupBox::title {
                color: #ddd;
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding-left: 10px;
                padding-right: 10px;
            }
            QCheckBox {
                color: #ddd;
            }
            QSlider::groove:horizontal {
                background: #555;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #888;
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -4px 0;
            }
            QSlider::handle:horizontal:hover {
                background: #999;
            }
            QSlider::handle:horizontal:pressed {
                background: #aaa;
            }
            QFrame {
                background-color: #555;
                height: 1px;
            }
        """)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 基本设置组
        basic_group = QGroupBox("基本设置")
        basic_layout = QVBoxLayout()
        
        # 字体选择
        font_layout = QHBoxLayout()
        font_label = QLabel("字体:")
        font_label.setMinimumWidth(100)
        self.combo_font = QComboBox()
        # 添加可用的字体选项
        self.combo_font.addItems([
            "SimHei", 
            "Microsoft YaHei", 
            "SimSun", 
            "KaiTi", 
            "FangSong",
            "Arial",
            "Times New Roman"
        ])
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.combo_font, 1)
        basic_layout.addLayout(font_layout)
        
        # 字体大小
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("字体大小:")
        font_size_label.setMinimumWidth(100)
        self.slider_font_size = QSlider(Qt.Orientation.Horizontal)
        self.slider_font_size.setRange(12, 36)
        self.slider_font_size.setValue(16)
        self.slider_font_size.setTickInterval(1)
        self.slider_font_size.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.label_font_size_value = QLabel("16")
        self.slider_font_size.valueChanged.connect(
            lambda value: self.label_font_size_value.setText(str(value))
        )
        font_size_layout.addWidget(font_size_label)
        font_size_layout.addWidget(self.slider_font_size, 1)
        font_size_layout.addWidget(self.label_font_size_value)
        basic_layout.addLayout(font_size_layout)
        
        # 行距
        line_spacing_layout = QHBoxLayout()
        line_spacing_label = QLabel("行距:")
        line_spacing_label.setMinimumWidth(100)
        self.slider_line_spacing = QSlider(Qt.Orientation.Horizontal)
        self.slider_line_spacing.setRange(1, 30)
        self.slider_line_spacing.setValue(5)
        self.slider_line_spacing.setTickInterval(1)
        self.slider_line_spacing.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.label_line_spacing_value = QLabel("5")
        self.slider_line_spacing.valueChanged.connect(
            lambda value: self.label_line_spacing_value.setText(str(value))
        )
        line_spacing_layout.addWidget(line_spacing_label)
        line_spacing_layout.addWidget(self.slider_line_spacing, 1)
        line_spacing_layout.addWidget(self.label_line_spacing_value)
        basic_layout.addLayout(line_spacing_layout)
        
        # 边距
        margin_layout = QHBoxLayout()
        margin_label = QLabel("页边距:")
        margin_label.setMinimumWidth(100)
        self.slider_margin = QSlider(Qt.Orientation.Horizontal)
        self.slider_margin.setRange(10, 100)
        self.slider_margin.setValue(30)
        self.slider_margin.setTickInterval(5)
        self.slider_margin.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.label_margin_value = QLabel("30")
        self.slider_margin.valueChanged.connect(
            lambda value: self.label_margin_value.setText(str(value))
        )
        margin_layout.addWidget(margin_label)
        margin_layout.addWidget(self.slider_margin, 1)
        margin_layout.addWidget(self.label_margin_value)
        basic_layout.addLayout(margin_layout)
        
        # 文本颜色
        text_color_layout = QHBoxLayout()
        text_color_label = QLabel("文本颜色:")
        text_color_label.setMinimumWidth(100)
        self.combo_text_color = QComboBox()
        self.combo_text_color.addItems(["黑色", "深灰色", "蓝色", "棕色", "绿色"])
        text_color_layout.addWidget(text_color_label)
        text_color_layout.addWidget(self.combo_text_color, 1)
        basic_layout.addLayout(text_color_layout)
        
        basic_group.setLayout(basic_layout)
        main_layout.addWidget(basic_group)
        
        # 手写效果组
        effect_group = QGroupBox("手写效果")
        effect_layout = QVBoxLayout()
        
        # 效果强度
        effect_strength_layout = QHBoxLayout()
        effect_strength_label = QLabel("效果强度:")
        effect_strength_label.setMinimumWidth(100)
        self.combo_effect_strength = QComboBox()
        self.combo_effect_strength.addItems(["无效果", "轻微", "自然", "强烈"])
        self.combo_effect_strength.setCurrentText("自然")
        effect_strength_layout.addWidget(effect_strength_label)
        effect_strength_layout.addWidget(self.combo_effect_strength, 1)
        effect_layout.addLayout(effect_strength_layout)
        
        # 随机偏移
        random_offset_layout = QHBoxLayout()
        random_offset_label = QLabel("随机偏移:")
        random_offset_label.setMinimumWidth(100)
        self.slider_random_offset = QSlider(Qt.Orientation.Horizontal)
        self.slider_random_offset.setRange(0, 10)
        self.slider_random_offset.setValue(3)
        self.slider_random_offset.setTickInterval(1)
        self.slider_random_offset.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.label_random_offset_value = QLabel("3")
        self.slider_random_offset.valueChanged.connect(
            lambda value: self.label_random_offset_value.setText(str(value))
        )
        random_offset_layout.addWidget(random_offset_label)
        random_offset_layout.addWidget(self.slider_random_offset, 1)
        random_offset_layout.addWidget(self.label_random_offset_value)
        effect_layout.addLayout(random_offset_layout)
        
        # 字间距随机
        char_spacing_layout = QHBoxLayout()
        char_spacing_label = QLabel("字间距随机:")
        char_spacing_label.setMinimumWidth(100)
        self.slider_char_spacing = QSlider(Qt.Orientation.Horizontal)
        self.slider_char_spacing.setRange(0, 5)
        self.slider_char_spacing.setValue(2)
        self.slider_char_spacing.setTickInterval(1)
        self.slider_char_spacing.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.label_char_spacing_value = QLabel("2")
        self.slider_char_spacing.valueChanged.connect(
            lambda value: self.label_char_spacing_value.setText(str(value))
        )
        char_spacing_layout.addWidget(char_spacing_label)
        char_spacing_layout.addWidget(self.slider_char_spacing, 1)
        char_spacing_layout.addWidget(self.label_char_spacing_value)
        effect_layout.addLayout(char_spacing_layout)
        
        # 倾斜度
        skew_layout = QHBoxLayout()
        skew_label = QLabel("倾斜度:")
        skew_label.setMinimumWidth(100)
        self.slider_skew = QSlider(Qt.Orientation.Horizontal)
        self.slider_skew.setRange(-10, 10)
        self.slider_skew.setValue(0)
        self.slider_skew.setTickInterval(1)
        self.slider_skew.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.label_skew_value = QLabel("0")
        self.slider_skew.valueChanged.connect(
            lambda value: self.label_skew_value.setText(str(value))
        )
        skew_layout.addWidget(skew_label)
        skew_layout.addWidget(self.slider_skew, 1)
        skew_layout.addWidget(self.label_skew_value)
        effect_layout.addLayout(skew_layout)
        
        effect_group.setLayout(effect_layout)
        main_layout.addWidget(effect_group)
        
        # 纸张效果组
        paper_group = QGroupBox("纸张效果")
        paper_layout = QVBoxLayout()
        
        # 纸张颜色
        paper_color_layout = QHBoxLayout()
        paper_color_label = QLabel("纸张颜色:")
        paper_color_label.setMinimumWidth(100)
        self.combo_paper_color = QComboBox()
        self.combo_paper_color.addItems(["白色", "米黄色", "浅灰色", "浅蓝色"])
        paper_color_layout.addWidget(paper_color_label)
        paper_color_layout.addWidget(self.combo_paper_color, 1)
        paper_layout.addLayout(paper_color_layout)
        
        # 纸张纹理
        paper_texture_layout = QHBoxLayout()
        paper_texture_label = QLabel("纸张纹理:")
        paper_texture_label.setMinimumWidth(100)
        self.combo_paper_texture = QComboBox()
        self.combo_paper_texture.addItems(["无", "轻微纸张纹理", "明显纸张纹理", "笔记本纸张"])
        paper_texture_layout.addWidget(paper_texture_label)
        paper_texture_layout.addWidget(self.combo_paper_texture, 1)
        paper_layout.addLayout(paper_texture_layout)
        
        # 墨水扩散效果
        ink_spread_layout = QHBoxLayout()
        self.checkbox_ink_spread = QCheckBox("墨水扩散效果")
        self.checkbox_ink_spread.setChecked(True)
        ink_spread_layout.addWidget(self.checkbox_ink_spread)
        paper_layout.addLayout(ink_spread_layout)
        
        # 对比度调整
        contrast_layout = QHBoxLayout()
        contrast_label = QLabel("对比度调整:")
        contrast_label.setMinimumWidth(100)
        self.slider_contrast = QSlider(Qt.Orientation.Horizontal)
        self.slider_contrast.setRange(-50, 50)
        self.slider_contrast.setValue(0)
        self.slider_contrast.setTickInterval(5)
        self.slider_contrast.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.label_contrast_value = QLabel("0")
        self.slider_contrast.valueChanged.connect(
            lambda value: self.label_contrast_value.setText(str(value))
        )
        contrast_layout.addWidget(contrast_label)
        contrast_layout.addWidget(self.slider_contrast, 1)
        contrast_layout.addWidget(self.label_contrast_value)
        paper_layout.addLayout(contrast_layout)
        
        paper_group.setLayout(paper_layout)
        main_layout.addWidget(paper_group)
        
        # 高级设置组
        advanced_group = QGroupBox("高级设置")
        advanced_layout = QVBoxLayout()
        
        # 页面大小
        page_size_layout = QHBoxLayout()
        page_size_label = QLabel("页面大小:")
        page_size_label.setMinimumWidth(100)
        self.combo_page_size = QComboBox()
        self.combo_page_size.addItems(["A5 横版", "A5 竖版", "A4 横版", "A4 竖版", "自定义"])
        page_size_layout.addWidget(page_size_label)
        page_size_layout.addWidget(self.combo_page_size, 1)
        advanced_layout.addLayout(page_size_layout)
        
        # 输出格式
        output_format_layout = QHBoxLayout()
        output_format_label = QLabel("输出格式:")
        output_format_label.setMinimumWidth(100)
        self.combo_output_format = QComboBox()
        self.combo_output_format.addItems(["PNG", "JPEG", "PDF"])
        output_format_layout.addWidget(output_format_label)
        output_format_layout.addWidget(self.combo_output_format, 1)
        advanced_layout.addLayout(output_format_layout)
        
        # 抗锯齿
        antialiasing_layout = QHBoxLayout()
        self.checkbox_antialiasing = QCheckBox("启用抗锯齿")
        self.checkbox_antialiasing.setChecked(True)
        antialiasing_layout.addWidget(self.checkbox_antialiasing)
        advanced_layout.addLayout(antialiasing_layout)
        
        advanced_group.setLayout(advanced_layout)
        main_layout.addWidget(advanced_group)
        
        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        btn_preview = QPushButton("预览效果")
        btn_preview.clicked.connect(self.on_preview)
        button_layout.addWidget(btn_preview)
        
        btn_reset = QPushButton("重置")
        btn_reset.clicked.connect(self.on_reset)
        button_layout.addWidget(btn_reset)
        
        btn_save = QPushButton("保存")
        btn_save.setObjectName("btn_save")
        btn_save.clicked.connect(self.on_save)
        button_layout.addWidget(btn_save)
        
        main_layout.addLayout(button_layout)
    
    def load_settings(self):
        """从配置管理器加载设置"""
        if self.config_manager:
            try:
                # 加载基本设置
                self.combo_font.setCurrentText(self.config_manager.get("font_family", "SimHei"))
                self.slider_font_size.setValue(int(self.config_manager.get("font_size", "16")))
                self.label_font_size_value.setText(str(self.slider_font_size.value()))
                self.slider_line_spacing.setValue(int(self.config_manager.get("line_spacing", "5")))
                self.label_line_spacing_value.setText(str(self.slider_line_spacing.value()))
                self.slider_margin.setValue(int(self.config_manager.get("margin", "30")))
                self.label_margin_value.setText(str(self.slider_margin.value()))
                self.combo_text_color.setCurrentText(self.config_manager.get("text_color", "黑色"))
                
                # 加载手写效果设置
                self.combo_effect_strength.setCurrentText(self.config_manager.get("effect_strength", "自然"))
                self.slider_random_offset.setValue(int(self.config_manager.get("random_offset", "3")))
                self.label_random_offset_value.setText(str(self.slider_random_offset.value()))
                self.slider_char_spacing.setValue(int(self.config_manager.get("char_spacing_random", "2")))
                self.label_char_spacing_value.setText(str(self.slider_char_spacing.value()))
                self.slider_skew.setValue(int(self.config_manager.get("skew", "0")))
                self.label_skew_value.setText(str(self.slider_skew.value()))
                
                # 加载纸张效果设置
                self.combo_paper_color.setCurrentText(self.config_manager.get("paper_color", "白色"))
                self.combo_paper_texture.setCurrentText(self.config_manager.get("paper_texture", "无"))
                self.checkbox_ink_spread.setChecked(self.config_manager.get("ink_spread", "true").lower() == "true")
                self.slider_contrast.setValue(int(self.config_manager.get("contrast", "0")))
                self.label_contrast_value.setText(str(self.slider_contrast.value()))
                
                # 加载高级设置
                self.combo_page_size.setCurrentText(self.config_manager.get("page_size", "A5 横版"))
                self.combo_output_format.setCurrentText(self.config_manager.get("output_format", "PNG"))
                self.checkbox_antialiasing.setChecked(self.config_manager.get("antialiasing", "true").lower() == "true")
                
            except Exception as e:
                logger.error(f"加载设置失败: {e}")
                QMessageBox.warning(self, "警告", "加载设置失败，使用默认值")
    
    def save_settings(self):
        """保存设置到配置管理器"""
        if self.config_manager:
            try:
                # 保存基本设置
                self.config_manager.set("font_family", self.combo_font.currentText())
                self.config_manager.set("font_size", str(self.slider_font_size.value()))
                self.config_manager.set("line_spacing", str(self.slider_line_spacing.value()))
                self.config_manager.set("margin", str(self.slider_margin.value()))
                self.config_manager.set("text_color", self.combo_text_color.currentText())
                
                # 保存手写效果设置
                self.config_manager.set("effect_strength", self.combo_effect_strength.currentText())
                self.config_manager.set("random_offset", str(self.slider_random_offset.value()))
                self.config_manager.set("char_spacing_random", str(self.slider_char_spacing.value()))
                self.config_manager.set("skew", str(self.slider_skew.value()))
                
                # 保存纸张效果设置
                self.config_manager.set("paper_color", self.combo_paper_color.currentText())
                self.config_manager.set("paper_texture", self.combo_paper_texture.currentText())
                self.config_manager.set("ink_spread", str(self.checkbox_ink_spread.isChecked()).lower())
                self.config_manager.set("contrast", str(self.slider_contrast.value()))
                
                # 保存高级设置
                self.config_manager.set("page_size", self.combo_page_size.currentText())
                self.config_manager.set("output_format", self.combo_output_format.currentText())
                self.config_manager.set("antialiasing", str(self.checkbox_antialiasing.isChecked()).lower())
                
                # 保存到文件
                self.config_manager.save()
                return True
            except Exception as e:
                logger.error(f"保存设置失败: {e}")
                return False
        return False
    
    def on_preview(self):
        """预览手写效果"""
        # 这里应该调用手写体生成器来生成预览
        # 暂时只是一个占位符
        QMessageBox.information(self, "提示", "预览功能正在开发中")
    
    def on_reset(self):
        """重置设置"""
        reply = QMessageBox.question(
            self, 
            "确认重置", 
            "确定要重置所有设置为默认值吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 重置为默认值
            self.combo_font.setCurrentText("SimHei")
            self.slider_font_size.setValue(16)
            self.label_font_size_value.setText("16")
            self.slider_line_spacing.setValue(5)
            self.label_line_spacing_value.setText("5")
            self.slider_margin.setValue(30)
            self.label_margin_value.setText("30")
            self.combo_text_color.setCurrentText("黑色")
            
            self.combo_effect_strength.setCurrentText("自然")
            self.slider_random_offset.setValue(3)
            self.label_random_offset_value.setText("3")
            self.slider_char_spacing.setValue(2)
            self.label_char_spacing_value.setText("2")
            self.slider_skew.setValue(0)
            self.label_skew_value.setText("0")
            
            self.combo_paper_color.setCurrentText("白色")
            self.combo_paper_texture.setCurrentText("无")
            self.checkbox_ink_spread.setChecked(True)
            self.slider_contrast.setValue(0)
            self.label_contrast_value.setText("0")
            
            self.combo_page_size.setCurrentText("A5 横版")
            self.combo_output_format.setCurrentText("PNG")
            self.checkbox_antialiasing.setChecked(True)
    
    def on_save(self):
        """保存设置并关闭对话框"""
        if self.save_settings():
            QMessageBox.information(self, "成功", "设置已保存")
            self.accept()
        else:
            QMessageBox.critical(self, "错误", "保存设置失败")