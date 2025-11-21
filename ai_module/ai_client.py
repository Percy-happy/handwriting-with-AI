"""
AI客户端模块
负责与不同的AI服务提供商进行交互，生成文本内容
"""
import time
import logging
from typing import Optional, Dict, Any
from .prompt_templates import PromptTemplates

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIClient:
    """AI客户端基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.prompt_templates = PromptTemplates()
        self.max_retries = 3
        self.retry_delay = 2  # 秒
    
    def generate_content(self, prompt: str, **kwargs) -> Optional[str]:
        """生成AI内容
        
        Args:
            prompt: 提示词
            **kwargs: 额外参数
            
        Returns:
            生成的内容或None
        """
        raise NotImplementedError("子类必须实现generate_content方法")
    
    def generate_with_template(self, template_name: str, **template_vars) -> Optional[str]:
        """使用模板生成内容
        
        Args:
            template_name: 模板名称
            **template_vars: 模板变量
            
        Returns:
            生成的内容或None
        """
        prompt = self.prompt_templates.get_template(template_name, **template_vars)
        if prompt:
            return self.generate_content(prompt)
        return None
    
    def _retry_with_backoff(self, func, *args, **kwargs):
        """带退避的重试机制"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                logger.warning(f"尝试 {attempt + 1} 失败: {str(e)}")
                
                # 如果是最后一次尝试，则不重试
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)  # 指数退避
                    logger.info(f"{delay}秒后重试...")
                    time.sleep(delay)
        
        logger.error(f"所有 {self.max_retries} 次尝试都失败了: {str(last_error)}")
        raise last_error

class OpenAIClient(AIClient):
    """OpenAI API客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "gpt-3.5-turbo")
        
        # 延迟导入openai，避免在没有安装openai包时出错
        self._openai = None
        
    def _ensure_openai(self):
        """确保openai模块已导入"""
        if self._openai is None:
            try:
                import openai
                self._openai = openai
                self._openai.api_key = self.api_key
            except ImportError:
                raise ImportError("请安装openai包: pip install openai")
    
    def generate_content(self, prompt: str, **kwargs) -> Optional[str]:
        """使用OpenAI API生成内容
        
        Args:
            prompt: 提示词
            **kwargs: 额外参数
            
        Returns:
            生成的内容或None
        """
        if not self.api_key:
            logger.error("OpenAI API密钥未设置")
            raise ValueError("OpenAI API密钥未设置")
        
        self._ensure_openai()
        
        # 准备API参数
        api_params = {
            "model": kwargs.get("model", self.model),
            "messages": [
                {"role": "system", "content": "你是一个专业的内容生成助手。请根据用户的要求生成高质量的内容。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
            "n": kwargs.get("n", 1),
            "stop": kwargs.get("stop", None),
            "top_p": kwargs.get("top_p", 1),
            "frequency_penalty": kwargs.get("frequency_penalty", 0),
            "presence_penalty": kwargs.get("presence_penalty", 0)
        }
        
        # 使用重试机制调用API
        def _api_call():
            try:
                response = self._openai.ChatCompletion.create(**api_params)
                # 只返回第一个响应
                return response.choices[0].message["content"].strip()
            except self._openai.error.RateLimitError:
                logger.warning("超出API速率限制")
                raise
            except self._openai.error.APIError as e:
                logger.error(f"API错误: {str(e)}")
                raise
            except self._openai.error.AuthenticationError:
                logger.error("API密钥无效")
                raise ValueError("API密钥无效")
            except Exception as e:
                logger.error(f"未知错误: {str(e)}")
                raise
        
        try:
            return self._retry_with_backoff(_api_call)
        except Exception as e:
            logger.error(f"生成内容失败: {str(e)}")
            return None
    
    def validate_api_key(self) -> bool:
        """验证API密钥是否有效"""
        if not self.api_key:
            return False
        
        self._ensure_openai()
        
        try:
            # 使用一个简单的请求来验证密钥
            response = self._openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "验证密钥"}],
                max_tokens=1
            )
            return True
        except Exception:
            return False
    
    def update_api_key(self, api_key: str):
        """更新API密钥"""
        self.api_key = api_key
        if self._openai:
            self._openai.api_key = api_key

class MockAIClient(AIClient):
    """模拟AI客户端，用于测试"""
    
    def generate_content(self, prompt: str, **kwargs) -> Optional[str]:
        """生成模拟内容"""
        return f"这是模拟生成的内容，基于提示：{prompt[:50]}..."
    
    def validate_api_key(self) -> bool:
        """模拟客户端总是返回True"""
        return True

def get_ai_client(config: Dict[str, Any]) -> AIClient:
    """获取AI客户端实例
    
    Args:
        config: AI配置
        
    Returns:
        AI客户端实例
    """
    provider = config.get("provider", "openai").lower()
    
    if provider == "openai":
        return OpenAIClient(config)
    elif provider == "mock":
        return MockAIClient(config)
    else:
        raise ValueError(f"不支持的AI提供商: {provider}")