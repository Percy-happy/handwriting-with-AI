#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama API 调用工具模块
提供与本地Ollama服务交互的功能
"""

import asyncio
from typing import List, Dict, Any, Generator, AsyncGenerator
from ollama import chat as ollama_chat
from ollama import generate as ollama_generate
from ollama import list as ollama_list
from ollama import Client, AsyncClient
from ollama import ChatResponse

class OllamaAPI:
    """
    Ollama API 封装类
    提供同步和异步的API调用方法
    """
    
    def __init__(self, host: str = "http://localhost:11434"):
        """
        初始化Ollama API客户端
        
        Args:
            host: Ollama服务地址
        """
        self.host = host
        self.client = Client(host=host)
        self.async_client = AsyncClient(host=host)
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        获取可用的模型列表
        
        Returns:
            模型列表，每个模型包含name等信息
        """
        try:
            print("正在调用ollama_list()获取模型列表...")
            result = ollama_list()
            
            # 详细记录API响应
            print(f"Ollama API响应类型: {type(result)}")
            if isinstance(result, dict):
                print(f"响应键: {list(result.keys())}")
                
                # 尝试多种可能的键名
                possible_keys = ['models', 'tags', 'data', 'result']
                found_models = None
                
                for key in possible_keys:
                    if key in result:
                        print(f"在响应中找到键 '{key}': {type(result[key])}")
                        if isinstance(result[key], list):
                            found_models = result[key]
                            print(f"找到 {len(found_models)} 个模型条目")
                            break
                
                if found_models is None:
                    print("警告: 未找到预期格式的模型列表")
                    # 打印完整响应以便调试
                    print(f"完整响应内容: {result}")
                    # 尝试直接使用客户端获取模型
                    print("尝试使用客户端的list方法...")
                    try:
                        client_result = self.client.list()
                        print(f"客户端list方法响应: {client_result}")
                        if isinstance(client_result, dict) and 'models' in client_result:
                            found_models = client_result['models']
                    except Exception as e:
                        print(f"客户端list方法失败: {e}")
                
                # 验证并过滤模型
                valid_models = []
                if found_models:
                    for i, model in enumerate(found_models):
                        if isinstance(model, dict):
                            print(f"模型 {i+1}: {list(model.keys())}")
                            # 支持name或model字段作为模型标识
                            if 'name' in model:
                                valid_models.append(model)
                                print(f"  ✓ 添加模型: {model['name']}")
                            elif 'model' in model:
                                # 标准化响应格式，确保有name字段
                                model['name'] = model['model']
                                valid_models.append(model)
                                print(f"  ✓ 添加模型 (使用model字段): {model['name']}")
                        else:
                            print(f"  ✗ 跳过非字典类型模型: {type(model)}")
                
                return valid_models
            else:
                print(f"错误: Ollama API返回了非字典类型响应: {result}")
                return []
                
        except Exception as e:
            print(f"获取模型列表失败: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def chat_completion(self, model: str, messages: List[Dict[str, str]], 
                       system_prompt: str = None) -> str:
        """
        同步聊天完成
        
        Args:
            model: 使用的模型名称
            messages: 消息历史，格式为[{"role": "user", "content": "消息内容"}]
            system_prompt: 系统提示词
        
        Returns:
            模型生成的响应内容
        """
        try:
            # 如果提供了系统提示词，添加到消息历史的开头
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages
            
            response = ollama_chat(model=model, messages=messages)
            return response['message']['content']
        except Exception as e:
            print(f"聊天完成失败: {e}")
            raise
    
    def chat_stream(self, model: str, messages: List[Dict[str, str]],
                   system_prompt: str = None) -> Generator[str, None, None]:
        """
        同步流式聊天响应
        
        Args:
            model: 使用的模型名称
            messages: 消息历史
            system_prompt: 系统提示词
        
        Yields:
            响应的每个部分内容
        """
        try:
            # 如果提供了系统提示词，添加到消息历史的开头
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages
            
            stream = ollama_chat(
                model=model,
                messages=messages,
                stream=True
            )
            
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
        except Exception as e:
            print(f"流式聊天响应失败: {e}")
            raise
    
    async def async_chat_completion(self, model: str, messages: List[Dict[str, str]],
                                  system_prompt: str = None) -> str:
        """
        异步聊天完成
        
        Args:
            model: 使用的模型名称
            messages: 消息历史
            system_prompt: 系统提示词
        
        Returns:
            模型生成的响应内容
        """
        try:
            # 如果提供了系统提示词，添加到消息历史的开头
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages
            
            response = await self.async_client.chat(model=model, messages=messages)
            return response['message']['content']
        except Exception as e:
            print(f"异步聊天完成失败: {e}")
            raise
    
    async def async_chat_stream(self, model: str, messages: List[Dict[str, str]],
                               system_prompt: str = None) -> AsyncGenerator[str, None]:
        """
        异步流式聊天响应
        
        Args:
            model: 使用的模型名称
            messages: 消息历史
            system_prompt: 系统提示词
        
        Yields:
            响应的每个部分内容
        """
        try:
            # 如果提供了系统提示词，添加到消息历史的开头
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages
            
            async for chunk in await self.async_client.chat(
                model=model,
                messages=messages,
                stream=True
            ):
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
        except Exception as e:
            print(f"异步流式聊天响应失败: {e}")
            raise

# 创建一个全局的Ollama API实例
ollama_api = OllamaAPI()

# 便捷函数
def get_ollama_models() -> List[str]:
    """
    获取可用的Ollama模型名称列表
    
    Returns:
        模型名称列表
    """
    try:
        print("调用get_ollama_models()...")
        model_names = []
        
        # 直接使用ollama.list()获取模型
        try:
            direct_result = ollama_list()
            print(f"直接调用ollama.list()结果: {direct_result}")
            print(f"直接调用返回类型: {type(direct_result)}")
            
            # 检查是否为Ollama特定的ListResponse类型
            if hasattr(direct_result, 'models'):
                print(f"检测到ListResponse类型，包含{len(direct_result.models)}个模型")
                for model in direct_result.models:
                    if hasattr(model, 'model'):
                        model_names.append(model.model)
                        print(f"添加模型名称: {model.model}")
                    elif hasattr(model, 'name'):
                        model_names.append(model.name)
                        print(f"添加模型名称: {model.name}")
                    elif isinstance(model, dict):
                        model_name = model.get('model') or model.get('name')
                        if model_name:
                            model_names.append(model_name)
                            print(f"添加模型名称: {model_name}")
                    else:
                        print(f"无法识别的模型对象: {type(model)}, 值: {model}")
            # 检查是否为字典类型
            elif isinstance(direct_result, dict):
                # 检查各种可能的模型列表位置
                for key in ['models', 'tags', 'data']:
                    if key in direct_result and isinstance(direct_result[key], list):
                        print(f"从键'{key}'获取到{len(direct_result[key])}个模型")
                        for model in direct_result[key]:
                            # 处理不同类型的模型对象
                            if isinstance(model, dict):
                                model_name = model.get('model') or model.get('name')
                                if model_name:
                                    model_names.append(model_name)
                                    print(f"添加模型名称: {model_name}")
                            elif hasattr(model, 'model'):
                                model_names.append(model.model)
                                print(f"添加模型名称: {model.model}")
                            elif hasattr(model, 'name'):
                                model_names.append(model.name)
                                print(f"添加模型名称: {model.name}")
                            elif isinstance(model, str):
                                model_names.append(model)
                                print(f"添加模型名称: {model}")
                            else:
                                print(f"未知的模型对象类型: {type(model)}, 值: {model}")
                        break
            else:
                print(f"ollama.list()返回的结果格式不符合预期: {direct_result}")
            
            if model_names:
                print(f"成功提取到模型名称: {model_names}")
                return model_names
            else:
                print("警告: 无法从ollama.list()结果中提取模型名称")
                
                # 备用方案：尝试直接导入ollama并使用
                try:
                    print("尝试直接导入ollama库...")
                    import ollama
                    direct_ollama_result = ollama.list()
                    print(f"直接使用ollama库结果: {direct_ollama_result}")
                    
                    if hasattr(direct_ollama_result, 'models'):
                        for model in direct_ollama_result.models:
                            if hasattr(model, 'model'):
                                model_names.append(model.model)
                                print(f"添加模型名称: {model.model}")
                except Exception as direct_error:
                    print(f"直接导入ollama库失败: {direct_error}")
        except Exception as e:
            print(f"直接调用ollama.list()失败: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"最终获取到 {len(model_names)} 个模型名称")
        if model_names:
            print(f"模型列表: {model_names}")
        
        return model_names
    except Exception as e:
        print(f"获取Ollama模型名称列表失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return []

def chat_with_ollama(model: str, prompt: str, system_prompt: str = None) -> str:
    """
    简单的Ollama聊天函数
    
    Args:
        model: 模型名称
        prompt: 用户提示词
        system_prompt: 系统提示词
    
    Returns:
        模型响应
    """
    messages = [{"role": "user", "content": prompt}]
    return ollama_api.chat_completion(model, messages, system_prompt)

def stream_chat_with_ollama(model: str, prompt: str, system_prompt: str = None) -> Generator[str, None, None]:
    """
    流式Ollama聊天函数
    
    Args:
        model: 模型名称
        prompt: 用户提示词
        system_prompt: 系统提示词
    
    Yields:
        响应的每个部分
    """
    messages = [{"role": "user", "content": prompt}]
    return ollama_api.chat_stream(model, messages, system_prompt)

# 示例系统提示词
DEFAULT_SYSTEM_PROMPT = """
你是一个手写体转换助手，专门用于帮助用户生成适合转换为手写体的文本内容。
请确保回复简洁明了，符合用户需求，并适合转换为手写体格式。
"""

TEXT_ENHANCEMENT_PROMPT = """
你是一个文本优化专家，请将用户提供的文本优化为更适合手写风格的格式。
请保持原意不变，但可以调整标点符号、段落分隔等，使其更易于阅读和手写。
"""

if __name__ == "__main__":
    # 简单的测试
    print("测试Ollama API...")
    
    # 获取可用模型
    models = get_ollama_models()
    print(f"可用模型: {models}")
    
    # 如果有可用模型，进行测试
    if models:
        model = models[0]  # 使用第一个可用模型
        print(f"使用模型: {model} 进行测试")
        
        # 测试同步调用
        try:
            response = chat_with_ollama(model, "你好，请介绍一下你自己")
            print(f"同步响应: {response}")
        except Exception as e:
            print(f"同步测试失败: {e}")
        
        # 测试流式调用
        print("流式响应:")
        try:
            for chunk in stream_chat_with_ollama(model, "请简要描述手写体的特点"):
                print(chunk, end="", flush=True)
            print()
        except Exception as e:
            print(f"流式测试失败: {e}")
    else:
        print("未找到可用的Ollama模型，请确保Ollama服务已启动并下载了模型。")
