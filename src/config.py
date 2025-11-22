#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手写体转换应用配置模块
提供样式自定义选项
"""

class HandwritingConfig:
    """
    手写体配置类
    用于存储和管理手写体生成的各种参数
    """
    def __init__(self):
        # 页面设置（A5横版，300dpi）
        self.page_width = int(210 * 300 / 25.4)  # 约2480像素
        self.page_height = int(148 * 300 / 25.4)  # 约1748像素
        
        # 字体设置
        self.font_path = None  # 自定义字体路径
        self.font_size = 120  # 字体大小（增大字号）
        self.fill = 0  # 文字颜色（0为黑色）
        
        # 排版设置
        self.left_margin = 100  # 左边距
        self.top_margin = 120  # 上边距（适当增加）
        self.right_margin = 100  # 右边距
        self.bottom_margin = 120  # 下边距（适当增加）
        
        # 间距设置
        self.line_spacing = 140  # 行间距（根据字体大小调整）
        self.word_spacing = 20  # 字间距（适当增加）
        self.letter_spacing = 0  # 字母间距
        
        # 随机扰动设置（控制手写自然度）
        self.line_spacing_sigma = 8  # 行间距随机扰动（适当增加）
        self.word_spacing_sigma = 3  # 字间距随机扰动（适当增加）
        self.letter_spacing_sigma = 0.5  # 字母间距随机扰动
        self.font_size_sigma = 3  # 字体大小随机扰动（适当增加）
    
    def update_from_dict(self, config_dict):
        """
        从字典更新配置
        
        Args:
            config_dict (dict): 包含配置参数的字典
        """
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """
        将配置转换为字典
        
        Returns:
            dict: 配置参数字典
        """
        return {
            "page_width": self.page_width,
            "page_height": self.page_height,
            "font_path": self.font_path,
            "font_size": self.font_size,
            "fill": self.fill,
            "left_margin": self.left_margin,
            "top_margin": self.top_margin,
            "right_margin": self.right_margin,
            "bottom_margin": self.bottom_margin,
            "line_spacing": self.line_spacing,
            "word_spacing": self.word_spacing,
            "letter_spacing": self.letter_spacing,
            "line_spacing_sigma": self.line_spacing_sigma,
            "word_spacing_sigma": self.word_spacing_sigma,
            "letter_spacing_sigma": self.letter_spacing_sigma,
            "font_size_sigma": self.font_size_sigma
        }

def get_preset_styles():
    """
    获取预设样式
    
    Returns:
        dict: 预设样式字典
    """
    presets = {
        "default": HandwritingConfig(),  # 默认样式
        "compact": HandwritingConfig(),  # 紧凑样式
        "neat": HandwritingConfig(),     # 整洁样式
        "casual": HandwritingConfig()    # 随意样式
    }
    
    # 配置紧凑样式
    presets["compact"].font_size = 36
    presets["compact"].line_spacing = 60
    presets["compact"].word_spacing = 5
    presets["compact"].left_margin = 80
    presets["compact"].right_margin = 80
    
    # 配置整洁样式
    presets["neat"].font_size_sigma = 1
    presets["neat"].line_spacing_sigma = 3
    presets["neat"].word_spacing_sigma = 1
    
    # 配置随意样式
    presets["casual"].font_size_sigma = 3
    presets["casual"].line_spacing_sigma = 10
    presets["casual"].word_spacing_sigma = 3
    presets["casual"].letter_spacing_sigma = 1
    
    return presets
