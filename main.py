"""
AI手写体生成应用 - 主入口文件
用于初始化和启动应用程序
"""
import sys
import os
import logging
import signal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QLocale, QTranslator
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("HandwritingAI")

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入应用程序组件
try:
    from config import ConfigManager
    from ui.main_window import MainWindow
    logger.info("成功导入应用程序组件")
except ImportError as e:
    logger.error(f"导入应用程序组件失败: {e}")
    sys.exit(1)

class HandwritingAIApp:
    """
    AI手写体生成应用程序类
    负责应用程序的初始化、配置和启动
    """
    
    def __init__(self):
        """初始化应用程序"""
        self.app = None
        self.config_manager = None
        self.main_window = None
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """设置信号处理器，用于优雅退出"""
        try:
            # 处理Ctrl+C信号
            signal.signal(signal.SIGINT, self.handle_interrupt)
            logger.info("成功设置信号处理器")
        except Exception as e:
            logger.warning(f"设置信号处理器失败: {e}")
    
    def handle_interrupt(self, signum, frame):
        """处理中断信号"""
        logger.info(f"收到中断信号 {signum}，正在退出...")
        if self.app:
            self.app.quit()
    
    def initialize_config(self):
        """初始化配置管理器"""
        try:
            self.config_manager = ConfigManager()
            self.config_manager.load()
            logger.info("成功初始化配置管理器")
            return True
        except Exception as e:
            logger.error(f"初始化配置管理器失败: {e}")
            return False
    
    def setup_appearance(self):
        """设置应用程序外观"""
        if not self.app:
            return
        
        try:
            # 设置应用程序信息
            self.app.setApplicationName("AI手写体生成器")
            self.app.setApplicationVersion("1.0.0")
            self.app.setOrganizationName("HandwritingAI")
            self.app.setOrganizationDomain("handwriting-ai.example.com")
            
            # 设置全局字体
            font_family = self.config_manager.get("app_font", "SimHei")
            font_size = int(self.config_manager.get("app_font_size", "10"))
            font = QFont(font_family, font_size)
            self.app.setFont(font)
            
            # 设置深色主题
            if self.config_manager.get("dark_theme", "true").lower() == "true":
                self.setup_dark_theme()
            
            logger.info("成功设置应用程序外观")
        except Exception as e:
            logger.error(f"设置应用程序外观失败: {e}")
    
    def setup_dark_theme(self):
        """设置深色主题"""
        if not self.app:
            return
        
        try:
            palette = QPalette()
            
            # 主色调
            palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(230, 230, 230))
            palette.setColor(QPalette.ColorRole.Base, QColor(40, 40, 40))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(50, 50, 50))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(40, 40, 40))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(230, 230, 230))
            palette.setColor(QPalette.ColorRole.Text, QColor(230, 230, 230))
            palette.setColor(QPalette.ColorRole.Button, QColor(50, 50, 50))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(230, 230, 230))
            palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
            
            # 禁用状态颜色
            palette.setColor(QPalette.ColorRole.Disabled, QPalette.ColorGroup.Normal, QPalette.ColorRole.ButtonText, QColor(100, 100, 100))
            palette.setColor(QPalette.ColorRole.Disabled, QPalette.ColorGroup.Normal, QPalette.ColorRole.WindowText, QColor(100, 100, 100))
            palette.setColor(QPalette.ColorRole.Disabled, QPalette.ColorGroup.Normal, QPalette.ColorRole.Text, QColor(100, 100, 100))
            palette.setColor(QPalette.ColorRole.Disabled, QPalette.ColorGroup.Normal, QPalette.ColorRole.Light, QColor(50, 50, 50))
            
            self.app.setPalette(palette)
            logger.info("成功设置深色主题")
        except Exception as e:
            logger.error(f"设置深色主题失败: {e}")
    
    def initialize_ui(self):
        """初始化用户界面"""
        try:
            # 创建主窗口
            self.main_window = MainWindow(config_manager=self.config_manager)
            
            # 设置窗口标题和图标
            self.main_window.setWindowTitle("AI手写体生成器 - v1.0.0")
            
            # 设置窗口尺寸
            window_width = int(self.config_manager.get("window_width", "1200"))
            window_height = int(self.config_manager.get("window_height", "800"))
            self.main_window.resize(window_width, window_height)
            
            # 居中显示
            screen_geometry = QApplication.primaryScreen().geometry()
            x = (screen_geometry.width() - window_width) // 2
            y = (screen_geometry.height() - window_height) // 2
            self.main_window.move(x, y)
            
            # 显示窗口
            self.main_window.show()
            logger.info("成功初始化用户界面")
            return True
        except Exception as e:
            logger.error(f"初始化用户界面失败: {e}")
            return False
    
    def save_settings_on_exit(self):
        """退出时保存设置"""
        try:
            if self.config_manager and self.main_window:
                # 保存窗口尺寸
                window_size = self.main_window.size()
                self.config_manager.set("window_width", str(window_size.width()))
                self.config_manager.set("window_height", str(window_size.height()))
                
                # 保存配置
                self.config_manager.save()
                logger.info("成功保存设置")
        except Exception as e:
            logger.error(f"保存设置失败: {e}")
    
    def run(self):
        """运行应用程序"""
        try:
            logger.info("开始启动AI手写体生成应用")
            
            # 创建QApplication实例
            self.app = QApplication(sys.argv)
            
            # 设置应用程序属性
            self.app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
            self.app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
            
            # 初始化配置
            if not self.initialize_config():
                logger.error("配置初始化失败，无法继续启动应用")
                return 1
            
            # 设置应用程序外观
            self.setup_appearance()
            
            # 初始化用户界面
            if not self.initialize_ui():
                logger.error("用户界面初始化失败，无法继续启动应用")
                return 1
            
            # 连接退出信号
            self.app.aboutToQuit.connect(self.save_settings_on_exit)
            
            logger.info("应用程序启动成功")
            
            # 运行应用程序事件循环
            return self.app.exec()
            
        except Exception as e:
            logger.error(f"应用程序启动失败: {e}")
            return 1
        finally:
            logger.info("应用程序已退出")

def main():
    """
    主函数
    应用程序的入口点
    """
    try:
        # 创建并运行应用程序
        app = HandwritingAIApp()
        exit_code = app.run()
        sys.exit(exit_code)
    except Exception as e:
        logger.critical(f"应用程序发生致命错误: {e}")
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()