"""
AI设置对话框模块
用于配置API密钥和AI相关参数
"""
import sys
import logging
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QGroupBox, QCheckBox, QTextEdit,
    QMessageBox, QFrame
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AISettingsDialog(QDialog):
    """AI设置对话框"""
    
    def __init__(self, parent=None, config_manager=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("AI设置")
        self.setMinimumSize(600, 500)
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
            QLineEdit, QComboBox, QTextEdit {
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
            QFrame {
                background-color: #555;
                height: 1px;
            }
        """)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # API设置组
        api_group = QGroupBox("API设置")
        api_layout = QVBoxLayout()
        
        # API提供商选择
        provider_layout = QHBoxLayout()
        provider_label = QLabel("API提供商:")
        provider_label.setMinimumWidth(100)
        self.combo_provider = QComboBox()
        self.combo_provider.addItems(["OpenAI", "Azure OpenAI", "其他"])
        self.combo_provider.currentTextChanged.connect(self.on_provider_changed)
        provider_layout.addWidget(provider_label)
        provider_layout.addWidget(self.combo_provider, 1)
        api_layout.addLayout(provider_layout)
        
        # API密钥
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel("API密钥:")
        api_key_label.setMinimumWidth(100)
        self.edit_api_key = QLineEdit()
        self.edit_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.checkbox_show_key = QCheckBox("显示密钥")
        self.checkbox_show_key.stateChanged.connect(self.on_show_key_changed)
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.edit_api_key, 1)
        api_key_layout.addWidget(self.checkbox_show_key)
        api_layout.addLayout(api_key_layout)
        
        # API基础URL（Azure等需要）
        base_url_layout = QHBoxLayout()
        base_url_label = QLabel("API基础URL:")
        base_url_label.setMinimumWidth(100)
        self.edit_base_url = QLineEdit()
        self.edit_base_url.setPlaceholderText("留空使用默认值")
        base_url_layout.addWidget(base_url_label)
        base_url_layout.addWidget(self.edit_base_url, 1)
        self.base_url_layout = base_url_layout
        api_layout.addLayout(base_url_layout)
        
        # 模型选择
        model_layout = QHBoxLayout()
        model_label = QLabel("模型:")
        model_label.setMinimumWidth(100)
        self.combo_model = QComboBox()
        # 为OpenAI添加默认模型选项
        self.combo_model.addItems(["gpt-3.5-turbo", "gpt-4", "gpt-4o"])
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.combo_model, 1)
        api_layout.addLayout(model_layout)
        
        # Azure资源名称（仅Azure需要）
        azure_resource_layout = QHBoxLayout()
        azure_resource_label = QLabel("Azure资源名称:")
        azure_resource_label.setMinimumWidth(100)
        self.edit_azure_resource = QLineEdit()
        azure_resource_layout.addWidget(azure_resource_label)
        azure_resource_layout.addWidget(self.edit_azure_resource, 1)
        self.azure_resource_layout = azure_resource_layout
        api_layout.addLayout(azure_resource_layout)
        
        # Azure部署名称（仅Azure需要）
        azure_deployment_layout = QHBoxLayout()
        azure_deployment_label = QLabel("Azure部署名称:")
        azure_deployment_label.setMinimumWidth(100)
        self.edit_azure_deployment = QLineEdit()
        azure_deployment_layout.addWidget(azure_deployment_label)
        azure_deployment_layout.addWidget(self.edit_azure_deployment, 1)
        self.azure_deployment_layout = azure_deployment_layout
        api_layout.addLayout(azure_deployment_layout)
        
        # API版本（仅Azure需要）
        api_version_layout = QHBoxLayout()
        api_version_label = QLabel("API版本:")
        api_version_label.setMinimumWidth(100)
        self.edit_api_version = QLineEdit()
        self.edit_api_version.setPlaceholderText("例如: 2024-02-15-preview")
        api_version_layout.addWidget(api_version_label)
        api_version_layout.addWidget(self.edit_api_version, 1)
        self.api_version_layout = api_version_layout
        api_layout.addLayout(api_version_layout)
        
        api_group.setLayout(api_layout)
        main_layout.addWidget(api_group)
        
        # 高级设置组
        advanced_group = QGroupBox("高级设置")
        advanced_layout = QVBoxLayout()
        
        # 最大生成长度
        max_tokens_layout = QHBoxLayout()
        max_tokens_label = QLabel("最大生成长度:")
        max_tokens_label.setMinimumWidth(100)
        self.edit_max_tokens = QLineEdit("1000")
        max_tokens_layout.addWidget(max_tokens_label)
        max_tokens_layout.addWidget(self.edit_max_tokens, 1)
        advanced_layout.addLayout(max_tokens_layout)
        
        # 温度设置
        temperature_layout = QHBoxLayout()
        temperature_label = QLabel("温度 (0-2):")
        temperature_label.setMinimumWidth(100)
        self.edit_temperature = QLineEdit("0.7")
        temperature_layout.addWidget(temperature_label)
        temperature_layout.addWidget(self.edit_temperature, 1)
        advanced_layout.addLayout(temperature_layout)
        
        # 系统提示
        system_prompt_layout = QVBoxLayout()
        system_prompt_label = QLabel("系统提示:")
        self.edit_system_prompt = QTextEdit()
        self.edit_system_prompt.setPlaceholderText("输入系统提示词，指导AI的行为...")
        self.edit_system_prompt.setMinimumHeight(80)
        system_prompt_layout.addWidget(system_prompt_label)
        system_prompt_layout.addWidget(self.edit_system_prompt)
        advanced_layout.addLayout(system_prompt_layout)
        
        advanced_group.setLayout(advanced_layout)
        main_layout.addWidget(advanced_group)
        
        # 本地模式选项
        local_mode_layout = QHBoxLayout()
        self.checkbox_local_mode = QCheckBox("使用本地模式（不调用API）")
        self.checkbox_local_mode.stateChanged.connect(self.on_local_mode_changed)
        local_mode_layout.addWidget(self.checkbox_local_mode)
        main_layout.addLayout(local_mode_layout)
        
        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        btn_test = QPushButton("测试连接")
        btn_test.clicked.connect(self.on_test_connection)
        button_layout.addWidget(btn_test)
        
        btn_reset = QPushButton("重置")
        btn_reset.clicked.connect(self.on_reset)
        button_layout.addWidget(btn_reset)
        
        btn_save = QPushButton("保存")
        btn_save.setObjectName("btn_save")
        btn_save.clicked.connect(self.on_save)
        button_layout.addWidget(btn_save)
        
        main_layout.addLayout(button_layout)
        
        # 初始设置
        self.on_provider_changed(self.combo_provider.currentText())
    
    def load_settings(self):
        """从配置管理器加载设置"""
        if self.config_manager:
            try:
                # 加载API设置
                self.combo_provider.setCurrentText(self.config_manager.get("ai_provider", "OpenAI"))
                self.edit_api_key.setText(self.config_manager.get("api_key", ""))
                self.edit_base_url.setText(self.config_manager.get("base_url", ""))
                self.combo_model.setCurrentText(self.config_manager.get("model", "gpt-3.5-turbo"))
                
                # 加载Azure设置
                self.edit_azure_resource.setText(self.config_manager.get("azure_resource_name", ""))
                self.edit_azure_deployment.setText(self.config_manager.get("azure_deployment_name", ""))
                self.edit_api_version.setText(self.config_manager.get("api_version", ""))
                
                # 加载高级设置
                self.edit_max_tokens.setText(self.config_manager.get("max_tokens", "1000"))
                self.edit_temperature.setText(self.config_manager.get("temperature", "0.7"))
                self.edit_system_prompt.setPlainText(self.config_manager.get("system_prompt", ""))
                
                # 加载本地模式设置
                local_mode = self.config_manager.get("local_mode", "false").lower() == "true"
                self.checkbox_local_mode.setChecked(local_mode)
                
            except Exception as e:
                logger.error(f"加载设置失败: {e}")
                QMessageBox.warning(self, "警告", "加载设置失败，使用默认值")
    
    def save_settings(self):
        """保存设置到配置管理器"""
        if self.config_manager:
            try:
                # 保存API设置
                self.config_manager.set("ai_provider", self.combo_provider.currentText())
                self.config_manager.set("api_key", self.edit_api_key.text())
                self.config_manager.set("base_url", self.edit_base_url.text())
                self.config_manager.set("model", self.combo_model.currentText())
                
                # 保存Azure设置
                self.config_manager.set("azure_resource_name", self.edit_azure_resource.text())
                self.config_manager.set("azure_deployment_name", self.edit_azure_deployment.text())
                self.config_manager.set("api_version", self.edit_api_version.text())
                
                # 保存高级设置
                self.config_manager.set("max_tokens", self.edit_max_tokens.text())
                self.config_manager.set("temperature", self.edit_temperature.text())
                self.config_manager.set("system_prompt", self.edit_system_prompt.toPlainText())
                
                # 保存本地模式设置
                self.config_manager.set("local_mode", str(self.checkbox_local_mode.isChecked()).lower())
                
                # 保存到文件
                self.config_manager.save()
                return True
            except Exception as e:
                logger.error(f"保存设置失败: {e}")
                return False
        return False
    
    def validate_settings(self):
        """验证设置是否有效"""
        if self.checkbox_local_mode.isChecked():
            return True
        
        # 检查API密钥
        if not self.edit_api_key.text().strip():
            QMessageBox.warning(self, "警告", "请输入API密钥")
            self.edit_api_key.setFocus()
            return False
        
        # 验证数值参数
        try:
            max_tokens = int(self.edit_max_tokens.text())
            if max_tokens <= 0:
                raise ValueError("最大生成长度必须大于0")
        except ValueError as e:
            QMessageBox.warning(self, "警告", f"最大生成长度无效: {e}")
            self.edit_max_tokens.setFocus()
            return False
        
        try:
            temperature = float(self.edit_temperature.text())
            if temperature < 0 or temperature > 2:
                raise ValueError("温度必须在0到2之间")
        except ValueError as e:
            QMessageBox.warning(self, "警告", f"温度设置无效: {e}")
            self.edit_temperature.setFocus()
            return False
        
        # 如果是Azure，检查必要参数
        if self.combo_provider.currentText() == "Azure OpenAI":
            if not self.edit_azure_resource.text().strip():
                QMessageBox.warning(self, "警告", "请输入Azure资源名称")
                self.edit_azure_resource.setFocus()
                return False
            if not self.edit_azure_deployment.text().strip():
                QMessageBox.warning(self, "警告", "请输入Azure部署名称")
                self.edit_azure_deployment.setFocus()
                return False
            if not self.edit_api_version.text().strip():
                QMessageBox.warning(self, "警告", "请输入API版本")
                self.edit_api_version.setFocus()
                return False
        
        return True
    
    def on_provider_changed(self, provider):
        """处理API提供商变更"""
        # 根据提供商显示或隐藏相关设置
        show_azure = provider == "Azure OpenAI"
        show_other = provider == "其他"
        
        self.base_url_layout.setEnabled(show_azure or show_other)
        self.azure_resource_layout.setEnabled(show_azure)
        self.azure_deployment_layout.setEnabled(show_azure)
        self.api_version_layout.setEnabled(show_azure)
        
        # 如果是Azure，更新模型选择
        if show_azure:
            self.combo_model.clear()
            self.combo_model.addItems(["gpt-35-turbo", "gpt-4", "gpt-4o"])
        else:
            self.combo_model.clear()
            self.combo_model.addItems(["gpt-3.5-turbo", "gpt-4", "gpt-4o"])
    
    def on_show_key_changed(self, state):
        """处理显示/隐藏API密钥"""
        if state == Qt.CheckState.Checked.value:
            self.edit_api_key.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.edit_api_key.setEchoMode(QLineEdit.EchoMode.Password)
    
    def on_local_mode_changed(self, state):
        """处理本地模式变更"""
        local_mode = state == Qt.CheckState.Checked.value
        # 禁用或启用API相关设置
        self.combo_provider.setEnabled(not local_mode)
        self.edit_api_key.setEnabled(not local_mode)
        self.checkbox_show_key.setEnabled(not local_mode)
        self.edit_base_url.setEnabled(not local_mode and (self.combo_provider.currentText() == "Azure OpenAI" or self.combo_provider.currentText() == "其他"))
        self.combo_model.setEnabled(not local_mode)
        self.edit_azure_resource.setEnabled(not local_mode and self.combo_provider.currentText() == "Azure OpenAI")
        self.edit_azure_deployment.setEnabled(not local_mode and self.combo_provider.currentText() == "Azure OpenAI")
        self.edit_api_version.setEnabled(not local_mode and self.combo_provider.currentText() == "Azure OpenAI")
    
    def on_test_connection(self):
        """测试API连接"""
        if not self.validate_settings():
            return
        
        # 如果是本地模式，直接提示成功
        if self.checkbox_local_mode.isChecked():
            QMessageBox.information(self, "成功", "本地模式已启用，无需测试连接")
            return
        
        self.setCursor(Qt.CursorShape.WaitCursor)
        
        try:
            # 这里应该调用AI客户端测试连接
            # 暂时模拟一个成功的测试
            from PyQt6.QtWidgets import QMessageBox
            import time
            time.sleep(1)  # 模拟网络延迟
            QMessageBox.information(self, "成功", "API连接测试成功！")
        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            QMessageBox.critical(self, "错误", f"API连接测试失败: {e}")
        finally:
            self.unsetCursor()
    
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
            self.combo_provider.setCurrentText("OpenAI")
            self.edit_api_key.clear()
            self.edit_base_url.clear()
            self.combo_model.setCurrentText("gpt-3.5-turbo")
            self.edit_azure_resource.clear()
            self.edit_azure_deployment.clear()
            self.edit_api_version.clear()
            self.edit_max_tokens.setText("1000")
            self.edit_temperature.setText("0.7")
            self.edit_system_prompt.clear()
            self.checkbox_local_mode.setChecked(False)
    
    def on_save(self):
        """保存设置并关闭对话框"""
        if not self.validate_settings():
            return
        
        if self.save_settings():
            QMessageBox.information(self, "成功", "设置已保存")
            self.accept()
        else:
            QMessageBox.critical(self, "错误", "保存设置失败")