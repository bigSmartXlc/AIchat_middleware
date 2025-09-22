import requests
import json
import time

# 中间件服务地址
BASE_URL = "http://localhost:8000/api"

# 测试发送普通消息
def test_send_message():
    """测试发送普通消息"""
    print("===== 测试发送普通消息 =====")
    url = f"{BASE_URL}/chat"
    data = {
        "user_id": "test_user_001",
        "messages": [
            {
                "role": "user",
                "content": "你好，我想了解一下你们的产品"
            }
        ],
        "model": "Qwen/QwQ-32B",
        "max_tokens": 200
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("请求成功！")
            print("响应内容:", json.dumps(response.json(), ensure_ascii=False, indent=2))
        else:
            print(f"请求失败: {response.status_code}")
            print("错误信息:", response.text)
    except Exception as e:
        print(f"发生异常: {str(e)}")

# 测试敏感词过滤
def test_sensitive_words():
    """测试敏感词过滤功能"""
    print("\n===== 测试敏感词过滤 =====")
    url = f"{BASE_URL}/chat"
    data = {
        "user_id": "test_user_002",
        "messages": [
            {
                "role": "user",
                "content": "这里有一些敏感词测试：政治、暴力、色情"
            }
        ],
        "model": "Qwen/QwQ-32B",
        "max_tokens": 200
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("请求成功！")
            print("响应内容:", json.dumps(response.json(), ensure_ascii=False, indent=2))
        else:
            print(f"请求失败: {response.status_code}")
            print("错误信息:", response.text)
    except Exception as e:
        print(f"发生异常: {str(e)}")

# 测试知识库集成
def test_knowledge_base():
    """测试知识库集成功能"""
    print("\n===== 测试知识库集成 =====")
    url = f"{BASE_URL}/chat"
    data = {
        "user_id": "test_user_003",
        "messages": [
            {
                "role": "user",
                "content": "请介绍一下你们公司"
            }
        ],
        "model": "Qwen/QwQ-32B",
        "max_tokens": 300
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("请求成功！")
            print("响应内容:", json.dumps(response.json(), ensure_ascii=False, indent=2))
        else:
            print(f"请求失败: {response.status_code}")
            print("错误信息:", response.text)
    except Exception as e:
        print(f"发生异常: {str(e)}")

# 测试获取聊天历史
def test_get_history():
    """测试获取聊天历史记录"""
    print("\n===== 测试获取聊天历史 =====")
    # 先发送一条消息，确保有历史记录
    test_send_message()
    time.sleep(1)  # 等待消息记录到数据库
    
    url = f"{BASE_URL}/history/test_user_001"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("获取历史成功！")
            print("历史记录:", json.dumps(response.json(), ensure_ascii=False, indent=2))
        else:
            print(f"获取历史失败: {response.status_code}")
            print("错误信息:", response.text)
    except Exception as e:
        print(f"发生异常: {str(e)}")

# 测试流式响应
def test_streaming_response():
    """测试流式响应功能"""
    print("\n===== 测试流式响应 =====")
    url = f"{BASE_URL}/chat/stream"
    data = {
        "user_id": "test_user_004",
        "messages": [
            {
                "role": "user",
                "content": "请写一个简短的故事，关于人工智能帮助人类"
            }
        ],
        "model": "Qwen/QwQ-32B",
        "max_tokens": 300,
        "stream": True
    }
    
    try:
        response = requests.post(url, json=data, stream=True)
        if response.status_code == 200:
            print("流式响应开始：")
            full_response = ""
            for line in response.iter_lines():
                if line:
                    # 解析SSE格式的响应
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        json_data = decoded_line[6:]
                        try:
                            data = json.loads(json_data)
                            content = data.get('content', '')
                            print(content, end='', flush=True)
                            full_response += content
                        except json.JSONDecodeError:
                            pass
            print("\n流式响应结束")
        else:
            print(f"请求失败: {response.status_code}")
            print("错误信息:", response.text)
    except Exception as e:
        print(f"发生异常: {str(e)}")

# 运行所有测试
def run_all_tests():
    """运行所有测试"""
    print("开始测试智能客服中间件...")
    
    # 注意：由于测试依赖于服务运行，这里只打印测试说明
    print("\n请确保中间件服务已经启动！")
    print("测试客户端功能说明：")
    print("1. test_send_message() - 测试发送普通消息")
    print("2. test_sensitive_words() - 测试敏感词过滤功能")
    print("3. test_knowledge_base() - 测试知识库集成功能")
    print("4. test_get_history() - 测试获取聊天历史记录")
    print("5. test_streaming_response() - 测试流式响应功能")
    
    print("\n您可以通过取消注释下面的函数调用来执行具体的测试。")
    
    # 取消下面的注释来运行具体的测试
    # test_send_message()
    # test_sensitive_words()
    # test_knowledge_base()
    # test_get_history()
    # test_streaming_response()

if __name__ == "__main__":
    run_all_tests()