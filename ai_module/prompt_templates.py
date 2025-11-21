"""
提示词模板管理模块
负责管理和提供各种提示词模板
"""
import logging
from typing import Dict, Optional

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptTemplates:
    """提示词模板管理类"""
    
    def __init__(self):
        # 预定义的提示词模板
        self.templates = {
            "测试笔记": {
                "description": "生成学习测试的笔记内容",
                "template": "请生成一段关于{topic}的学习笔记，内容要详细、专业，适合学生复习使用。\n\n要求：\n1. 包含核心概念解释\n2. 提供示例\n3. 添加关键点总结\n4. 语言通俗易懂\n\n请以正式但不生硬的语气撰写。"
            },
            "工作汇报": {
                "description": "生成工作进展汇报",
                "template": "请生成一份关于{project_name}项目的工作汇报。\n\n汇报要点：\n1. 当前项目进展情况\n2. 已完成的主要工作\n3. 遇到的问题和解决方案\n4. 下一步工作计划\n5. 需要协调的资源\n\n请使用专业、简洁的商务语言，突出重点和成果。"
            },
            "会议记录": {
                "description": "生成会议记录",
                "template": "请根据以下会议信息生成一份正式的会议记录：\n\n会议主题：{meeting_topic}\n会议日期：{meeting_date}\n参会人员：{attendees}\n\n请包含以下内容：\n1. 会议背景和目标\n2. 讨论的主要议题\n3. 达成的共识和决定\n4. 分配的任务和负责人\n5. 下次会议安排\n\n记录应简洁明了，条理清晰，便于后续查阅和执行。"
            },
            "读书笔记": {
                "description": "生成书籍章节的读书笔记",
                "template": "请为《{book_title}》的第{chapter}章生成一份读书笔记。\n\n笔记应包含：\n1. 章节主要内容概括\n2. 重要观点和论据\n3. 值得思考的问题\n4. 可实践的要点\n5. 个人感悟或评价\n\n请以个人阅读笔记的风格撰写，真实自然，体现对内容的理解和思考。"
            },
            "日记模板": {
                "description": "生成日记内容",
                "template": "请生成一篇关于{date}的日记，记录当天的主要活动和感受。\n\n日记内容：\n1. 天气和基本情况\n2. 主要活动和经历\n3. 遇见的人和事\n4. 心情和思考\n5. 明天的计划\n\n请使用真实、生动的语言，体现个人的情感和观察。"
            }
        }
        
        # 模板分类
        self.categories = {
            "学习": ["测试笔记", "读书笔记"],
            "工作": ["工作汇报", "会议记录"],
            "个人": ["日记模板"]
        }
    
    def get_template(self, template_name: str, **kwargs) -> Optional[str]:
        """获取并填充模板
        
        Args:
            template_name: 模板名称
            **kwargs: 模板变量
            
        Returns:
            填充后的模板内容或None
        """
        if template_name not in self.templates:
            logger.warning(f"模板 {template_name} 不存在")
            return None
        
        template = self.templates[template_name]["template"]
        
        try:
            # 尝试填充模板变量
            filled_template = template.format(**kwargs)
            return filled_template
        except KeyError as e:
            logger.error(f"模板变量缺失: {e}")
            return None
        except Exception as e:
            logger.error(f"填充模板时出错: {e}")
            return None
    
    def get_template_description(self, template_name: str) -> Optional[str]:
        """获取模板描述
        
        Args:
            template_name: 模板名称
            
        Returns:
            模板描述或None
        """
        if template_name in self.templates:
            return self.templates[template_name]["description"]
        return None
    
    def get_all_templates(self) -> Dict[str, Dict[str, str]]:
        """获取所有模板
        
        Returns:
            模板字典
        """
        return self.templates.copy()
    
    def get_template_names(self) -> list:
        """获取所有模板名称
        
        Returns:
            模板名称列表
        """
        return list(self.templates.keys())
    
    def add_template(self, name: str, description: str, template: str) -> bool:
        """添加自定义模板
        
        Args:
            name: 模板名称
            description: 模板描述
            template: 模板内容
            
        Returns:
            是否添加成功
        """
        if name in self.templates:
            logger.warning(f"模板 {name} 已存在")
            return False
        
        self.templates[name] = {
            "description": description,
            "template": template
        }
        
        # 将新模板添加到"自定义"分类
        if "自定义" not in self.categories:
            self.categories["自定义"] = []
        
        if name not in self.categories["自定义"]:
            self.categories["自定义"].append(name)
        
        logger.info(f"成功添加模板: {name}")
        return True
    
    def update_template(self, name: str, description: str = None, template: str = None) -> bool:
        """更新模板
        
        Args:
            name: 模板名称
            description: 模板描述（可选）
            template: 模板内容（可选）
            
        Returns:
            是否更新成功
        """
        if name not in self.templates:
            logger.warning(f"模板 {name} 不存在")
            return False
        
        if description is not None:
            self.templates[name]["description"] = description
        
        if template is not None:
            self.templates[name]["template"] = template
        
        logger.info(f"成功更新模板: {name}")
        return True
    
    def delete_template(self, name: str) -> bool:
        """删除模板
        
        Args:
            name: 模板名称
            
        Returns:
            是否删除成功
        """
        if name not in self.templates:
            logger.warning(f"模板 {name} 不存在")
            return False
        
        # 检查是否为预定义模板
        predefined_templates = ["测试笔记", "工作汇报", "会议记录", "读书笔记", "日记模板"]
        if name in predefined_templates:
            logger.warning(f"不能删除预定义模板: {name}")
            return False
        
        # 从分类中移除
        for category, templates in self.categories.items():
            if name in templates:
                templates.remove(name)
        
        # 删除模板
        del self.templates[name]
        logger.info(f"成功删除模板: {name}")
        return True
    
    def get_templates_by_category(self, category: str) -> list:
        """按分类获取模板
        
        Args:
            category: 分类名称
            
        Returns:
            模板名称列表
        """
        return self.categories.get(category, []).copy()
    
    def get_all_categories(self) -> list:
        """获取所有分类
        
        Returns:
            分类名称列表
        """
        return list(self.categories.keys())
    
    def search_templates(self, keyword: str) -> list:
        """搜索模板
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的模板名称列表
        """
        matched_templates = []
        keyword = keyword.lower()
        
        for name, data in self.templates.items():
            if (keyword in name.lower() or 
                keyword in data["description"].lower() or 
                keyword in data["template"].lower()):
                matched_templates.append(name)
        
        return matched_templates
    
    def validate_template(self, template: str) -> bool:
        """验证模板格式是否正确
        
        Args:
            template: 模板内容
            
        Returns:
            是否有效
        """
        try:
            # 检查模板中的变量格式是否正确
            # 简单检查：确保所有的{变量名}格式正确
            import re
            # 匹配所有 {变量名} 模式，变量名只能包含字母、数字、下划线
            variables = re.findall(r'\\{(\\w+)\\}', template)
            
            # 尝试使用这些变量创建一个字典并格式化模板
            # 这只是一个简单的验证，不能捕获所有可能的错误
            test_vars = {var: f"{var}_test_value" for var in variables}
            test_template = template.format(**test_vars)
            
            return True
        except Exception as e:
            logger.error(f"模板格式错误: {e}")
            return False