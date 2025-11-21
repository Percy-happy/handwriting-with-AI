"""
AI手写体生成应用 - 配置管理模块
用于处理应用程序的配置加载、保存和管理
"""
import os
import json
import logging
import uuid
import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from pathlib import Path

logger = logging.getLogger("HandwritingAI.Config")

class ConfigManager:
    """
    配置管理器类
    负责应用程序配置的读取、保存和访问
    """
    
    def __init__(self, config_file: str = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径，如果为None则使用默认路径
        """
        # 设置配置文件路径
        if config_file is None:
            self.config_file = Path("config.json")
        else:
            self.config_file = Path(config_file)
        
        self.env_file = Path(".env")
        
        # 默认配置 - 扁平化结构便于直接访问
        self.default_config = {
            # 应用程序设置
            "app_font": "SimHei",
            "app_font_size": "10",
            "dark_theme": "true",
            "window_width": "1200",
            "window_height": "800",
            
            # AI设置
            "ai_provider": "openai",  # openai, azure, local
            "api_key": "",
            "api_base_url": "https://api.openai.com/v1",
            "api_version": "",
            "model": "gpt-3.5-turbo",
            "max_tokens": "1000",
            "temperature": "0.7",
            "max_retries": "3",
            "timeout": "30",
            "system_prompt": "你是一位专业的写手，擅长将内容转换为自然流畅的手写体风格文本。请保持原文的意思不变，对语言进行适当润色，使其更符合手写体的特点。",
            
            # 手写体设置
            "font_family": "Ma Shan Zheng",
            "font_size": "12",
            "line_spacing": "1.5",
            "margin_left": "20",
            "margin_top": "20",
            "margin_right": "20",
            "margin_bottom": "20",
            "text_color": "#000000",
            "background_color": "#FFFFFF",
            "page_width": "148",  # A5宽度，单位mm
            "page_height": "210",  # A5高度，单位mm
            "output_dpi": "300",
            
            # 手写效果设置
            "handwriting_style": "natural",  # none, limited, natural, strong
            "random_offset_x": "2",
            "random_offset_y": "1",
            "letter_spacing_variation": "0.1",
            "line_rotation": "0.5",
            
            # 纸张效果设置
            "paper_texture": "none",  # none, light, medium, heavy
            "ink_spread": "0.2",
            "noise_level": "0.1",
            "brightness_adjust": "0",
            "contrast_adjust": "0",
            
            # 导出设置
            "export_format": "png",  # png, jpeg, pdf
            "export_quality": "90",
            "export_path": "",
            "add_watermark": "false",
            "watermark_text": "HandwritingAI",
            
            # 文本处理设置
            "auto_line_break": "true",
            "max_chars_per_line": "30",
            "paragraph_spacing": "2",
            "indent_first_line": "true",
            "indent_size": "2",
            
            # 模板历史记录
            "template_history": []
        }
        
        # 加载配置
        self.config = self.default_config.copy()
        self.load()
        self.load_env()
    
    def load(self) -> bool:
        """
        从配置文件加载配置
        
        Returns:
            bool: 加载是否成功
        """
        try:
            # 检查配置文件是否存在
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    
                    # 更新配置，保留默认值
                    if isinstance(loaded_config, dict):
                        # 处理旧格式配置（嵌套结构）
                        if 'ai_config' in loaded_config:
                            self._migrate_from_old_format(loaded_config)
                        else:
                            self.config.update(loaded_config)
                    logger.info(f"成功从 {self.config_file} 加载配置")
            else:
                # 使用默认配置
                self.config = self.default_config.copy()
                logger.info(f"配置文件不存在，使用默认配置")
                # 保存默认配置到文件
                self.save()
            
            # 验证并合并默认配置（确保所有必要的配置项都存在）
            self._validate_and_merge_defaults()
            
            return True
        except json.JSONDecodeError as e:
            logger.error(f"解析配置文件失败: {e}")
            # 使用默认配置
            self.config = self.default_config.copy()
            return False
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            # 使用默认配置
            self.config = self.default_config.copy()
            return False
    
    def _migrate_from_old_format(self, old_config: Dict[str, Any]) -> None:
        """
        从旧格式配置迁移到新格式
        
        Args:
            old_config: 旧格式配置字典
        """
        logger.info("检测到旧格式配置，正在迁移到新格式...")
        
        # 迁移AI配置
        if 'ai_config' in old_config:
            ai = old_config['ai_config']
            self.set('ai_provider', ai.get('provider', 'openai'))
            self.set('api_key', ai.get('api_key', ''))
            self.set('model', ai.get('model', 'gpt-3.5-turbo'))
        
        # 迁移手写体配置
        if 'handwriting_config' in old_config:
            hw = old_config['handwriting_config']
            self.set('font_size', str(hw.get('font_size', 12)))
            self.set('line_spacing', str(hw.get('line_spacing', 1.5)))
            margin = hw.get('margin', 10)
            self.set('margin_left', str(margin))
            self.set('margin_top', str(margin))
            self.set('margin_right', str(margin))
            self.set('margin_bottom', str(margin))
            self.set('handwriting_style', hw.get('effect_style', 'limited'))
        
        # 迁移UI配置
        if 'ui_config' in old_config:
            ui = old_config['ui_config']
            theme = ui.get('theme', 'dark')
            self.set('dark_theme', 'true' if theme == 'dark' else 'false')
        
        # 迁移模板历史
        if 'template_history' in old_config:
            self.set('template_history', old_config['template_history'])
    
    def save(self) -> bool:
        """
        将配置保存到文件
        
        Returns:
            bool: 保存是否成功
        """
        try:
            # 确保配置目录存在
            config_dir = self.config_file.parent
            if not config_dir.exists():
                config_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"创建配置目录: {config_dir}")
            
            # 保存配置时不包含API密钥，密钥保存在.env文件中
            config_to_save = self.config.copy()
            if "api_key" in config_to_save:
                config_to_save["api_key"] = ""
            
            # 保存配置到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=4, ensure_ascii=False)
            
            logger.info(f"成功保存配置到 {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False
    
    def load_env(self):
        """从.env文件加载环境变量"""
        load_dotenv(self.env_file)
        
        # 从环境变量加载API密钥
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key:
            self.set("api_key", api_key)
            logger.info("成功从环境变量加载API密钥")
    
    def save_api_key(self, api_key: str) -> bool:
        """
        保存API密钥到.env文件
        
        Args:
            api_key: API密钥
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 先读取现有内容
            env_content = ""
            if self.env_file.exists():
                with open(self.env_file, 'r') as f:
                    env_content = f.read()
            
            # 更新或添加API密钥
            lines = env_content.splitlines()
            new_lines = []
            key_found = False
            
            for line in lines:
                if line.startswith("OPENAI_API_KEY="):
                    new_lines.append(f"OPENAI_API_KEY={api_key}")
                    key_found = True
                else:
                    new_lines.append(line)
            
            if not key_found:
                new_lines.append(f"OPENAI_API_KEY={api_key}")
            
            # 写回文件
            with open(self.env_file, 'w') as f:
                f.write('\n'.join(new_lines))
            
            # 更新内存中的配置
            self.set("api_key", api_key)
            logger.info("成功保存API密钥到环境变量文件")
            return True
        except IOError as e:
            logger.error(f"无法保存API密钥到 {self.env_file}: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置项键名
            default: 默认值，如果配置项不存在则返回
            
        Returns:
            Any: 配置值或默认值
        """
        # 支持旧格式的点表示法作为兼容
        if '.' in key:
            keys = key.split('.')
            value = self.config
            
            try:
                for k in keys:
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        return default
                return value
            except (KeyError, TypeError):
                return default
        
        # 新格式直接访问
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置项键名
            value: 配置值
        """
        # 支持旧格式的点表示法作为兼容
        if '.' in key:
            keys = key.split('.')
            config = self.config
            
            # 导航到目标键的父级
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # 设置值
            config[keys[-1]] = value
        else:
            # 新格式直接设置
            self.config[key] = value
    
    def add_template_history(self, template_name: str, prompt: str) -> None:
        """
        添加模板到历史记录
        
        Args:
            template_name: 模板名称
            prompt: 提示词内容
        """
        template = {
            "id": str(uuid.uuid4())[:8],
            "name": template_name,
            "prompt": prompt,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # 确保template_history存在
        if "template_history" not in self.config:
            self.config["template_history"] = []
        
        self.config["template_history"].insert(0, template)
        # 限制历史记录数量
        if len(self.config["template_history"]) > 50:
            self.config["template_history"] = self.config["template_history"][:50]
        
        self.save()
        logger.info(f"添加模板历史: {template_name}")
    
    def get_all(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        return self.config.copy()
    
    def set_all(self, config: Dict[str, Any]) -> None:
        """
        设置所有配置
        
        Args:
            config: 新的配置字典
        """
        self.config = config.copy()
        # 验证并合并默认配置
        self._validate_and_merge_defaults()
    
    def reset_to_defaults(self) -> None:
        """
        重置为默认配置
        """
        self.config = self.default_config.copy()
        logger.info("已重置为默认配置")
    
    def _validate_and_merge_defaults(self) -> None:
        """
        验证并合并默认配置
        确保所有必要的配置项都存在
        """
        for key, default_value in self.default_config.items():
            if key not in self.config:
                self.config[key] = default_value
                logger.debug(f"配置项 {key} 缺失，使用默认值")
    
    def get_ai_settings(self) -> Dict[str, Any]:
        """
        获取AI相关配置
        
        Returns:
            Dict[str, Any]: AI配置字典
        """
        ai_keys = [
            "ai_provider", "api_key", "api_base_url", 
            "api_version", "model", "max_tokens", 
            "temperature", "max_retries", "timeout", 
            "system_prompt"
        ]
        return {key: self.get(key) for key in ai_keys}
    
    def get_handwriting_settings(self) -> Dict[str, Any]:
        """
        获取手写体相关配置
        
        Returns:
            Dict[str, Any]: 手写体配置字典
        """
        handwriting_keys = [
            "font_family", "font_size", "line_spacing",
            "margin_left", "margin_top", "margin_right",
            "margin_bottom", "text_color", "background_color",
            "page_width", "page_height", "output_dpi"
        ]
        return {key: self.get(key) for key in handwriting_keys}
    
    def get_effect_settings(self) -> Dict[str, Any]:
        """
        获取效果相关配置
        
        Returns:
            Dict[str, Any]: 效果配置字典
        """
        effect_keys = [
            "handwriting_style", "random_offset_x", "random_offset_y",
            "letter_spacing_variation", "line_rotation",
            "paper_texture", "ink_spread", "noise_level",
            "brightness_adjust", "contrast_adjust"
        ]
        return {key: self.get(key) for key in effect_keys}
    
    def get_export_settings(self) -> Dict[str, Any]:
        """
        获取导出相关配置
        
        Returns:
            Dict[str, Any]: 导出配置字典
        """
        export_keys = [
            "export_format", "export_quality", "export_path",
            "add_watermark", "watermark_text"
        ]
        return {key: self.get(key) for key in export_keys}
    
    def get_text_processing_settings(self) -> Dict[str, Any]:
        """
        获取文本处理相关配置
        
        Returns:
            Dict[str, Any]: 文本处理配置字典
        """
        text_keys = [
            "auto_line_break", "max_chars_per_line",
            "paragraph_spacing", "indent_first_line",
            "indent_size"
        ]
        return {key: self.get(key) for key in text_keys}
    
    def update_ai_settings(self, ai_settings: Dict[str, Any]) -> None:
        """
        更新AI相关配置
        
        Args:
            ai_settings: AI配置字典
        """
        for key, value in ai_settings.items():
            if key in self.config:
                self.set(key, value)
    
    def update_handwriting_settings(self, handwriting_settings: Dict[str, Any]) -> None:
        """
        更新手写体相关配置
        
        Args:
            handwriting_settings: 手写体配置字典
        """
        for key, value in handwriting_settings.items():
            if key in self.config:
                self.set(key, value)
    
    def update_effect_settings(self, effect_settings: Dict[str, Any]) -> None:
        """
        更新效果相关配置
        
        Args:
            effect_settings: 效果配置字典
        """
        for key, value in effect_settings.items():
            if key in self.config:
                self.set(key, value)
    
    def update_export_settings(self, export_settings: Dict[str, Any]) -> None:
        """
        更新导出相关配置
        
        Args:
            export_settings: 导出配置字典
        """
        for key, value in export_settings.items():
            if key in self.config:
                self.set(key, value)
    
    def update_text_processing_settings(self, text_settings: Dict[str, Any]) -> None:
        """
        更新文本处理相关配置
        
        Args:
            text_settings: 文本处理配置字典
        """
        for key, value in text_settings.items():
            if key in self.config:
                self.set(key, value)
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        递归合并配置字典
        
        Args:
            default: 默认配置
            user: 用户配置
            
        Returns:
            Dict[str, Any]: 合并后的配置
        """
        if not isinstance(user, dict):
            return default
        
        merged = default.copy()
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged

# 创建全局配置管理器实例
config_manager = ConfigManager()