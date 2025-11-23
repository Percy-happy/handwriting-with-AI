#!/usr/bin/env python3
# 测试Ollama API连接状态

import ollama
import socket
import time
import sys
from contextlib import contextmanager

@contextmanager
def timeout(seconds):
    """超时上下文管理器"""
    old_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(seconds)
    try:
        yield
    finally:
        socket.setdefaulttimeout(old_timeout)

print("开始测试Ollama API连接...")
print(f"使用的Python版本: {sys.version}")
print("使用的ollama库: 已导入")

# 测试1: 检查API连接
print("\n测试1: 检查API连接...")
try:
    with timeout(5):
        response = ollama.list()
        print(f"✓ 成功连接到Ollama API")
        print(f"API响应: {response}")
        
        # 检查是否有模型
        if 'models' in response and isinstance(response['models'], list):
            models = response['models']
            print(f"\n发现 {len(models)} 个模型:")
            for i, model in enumerate(models, 1):
                print(f"  {i}. 名称: {model.get('name', '未知')}")
                print(f"     模型ID: {model.get('model', '未知')}")
                print(f"     大小: {model.get('size', '未知')}")
                print(f"     详情: {model}")
        else:
            print("! 未找到模型列表或格式不正确")
            print(f"响应格式: {response.keys() if isinstance(response, dict) else type(response)}")
            
            # 打印原始响应以调试
            print(f"原始响应内容: {response}")
            
            # 尝试不同的键名
            print("\n尝试检查其他可能的键名...")
            if isinstance(response, dict):
                for key, value in response.items():
                    print(f"  键: {key}, 类型: {type(value)}")
                    if isinstance(value, list):
                        print(f"     列表长度: {len(value)}")
                        if value and isinstance(value[0], dict):
                            print(f"     列表项1键: {list(value[0].keys())}")

# 捕获超时异常
except socket.timeout:
    print("✗ 连接Ollama服务超时")
    print("请检查:")
    print("1. Ollama服务是否正在运行 (执行 'ollama serve' 启动)")
    print("2. Ollama服务是否监听在默认端口")
    print("3. 网络连接是否正常")

# 捕获连接异常
except ConnectionRefusedError:
    print("✗ 连接被拒绝")
    print("Ollama服务似乎没有运行，请执行 'ollama serve' 启动服务")

# 捕获其他异常
except Exception as e:
    print(f"✗ 测试API连接时发生错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# 测试2: 尝试拉取模型
try:
    print("\n测试2: 尝试列出可用模型信息...")
    # 尝试使用不同的方式获取模型
    # 1. 原始API调用方式
    import requests
    try:
        url = "http://localhost:11434/api/tags"
        resp = requests.get(url, timeout=3)
        print(f"直接API调用 (http://localhost:11434/api/tags): 状态码 {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"直接API响应: {data}")
    except Exception as e:
        print(f"直接API调用失败: {e}")

    # 2. 检查ollama库的导入路径
    print("\n检查ollama库导入路径:")
    print(f"ollama模块路径: {ollama.__file__}")

    # 3. 尝试模型列表的另一种方式
    print("\n尝试获取模型信息...")
    try:
        # 尝试通过api_tags直接获取
        import inspect
        print(f"ollama模块可用函数: {[func for func in dir(ollama) if not func.startswith('_')]}")
        
        # 尝试检查是否有tags方法
        if hasattr(ollama, 'tags'):
            tags = ollama.tags()
            print(f"使用ollama.tags(): {tags}")
    except Exception as e:
        print(f"获取模型信息失败: {e}")

    # 4. 检查服务进程
    print("\n检查Ollama服务进程...")
    import subprocess
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        ollama_processes = [line for line in result.stdout.split('\n') if 'ollama' in line]
        print(f"找到 {len(ollama_processes)} 个Ollama相关进程:")
        for process in ollama_processes:
            print(f"  {process.strip()}")
    except Exception as e:
        print(f"检查进程失败: {e}")

except Exception as e:
    print(f"测试2发生错误: {e}")

print("\n测试完成!")
