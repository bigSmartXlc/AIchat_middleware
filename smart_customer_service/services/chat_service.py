import os
import uuid
import litellm
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime
from models.chat_models import ChatRequest, ChatResponse, Message
from services.sensitive_word_service import filter_sensitive_words
from services.knowledge_base_service import attach_knowledge_to_query
from database.database import get_db, ChatHistory

# 配置LiteLLM
def configure_litellm():
    """配置LiteLLM，设置API密钥和其他参数"""
    import os
    
    # 从环境变量加载API密钥
    if os.getenv("OPENAI_API_KEY"):
        litellm.openai_key = os.getenv("OPENAI_API_KEY")
    if os.getenv("ANTHROPIC_API_KEY"):
        litellm.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    

# 初始化LiteLLM配置
# configure_litellm()

def process_chat_request(request: ChatRequest, stream: bool = False) -> Any:
    """
    处理聊天请求
    
    参数:
        request: 聊天请求对象
        stream: 是否使用流式响应
    
    返回:
        ChatResponse: 聊天响应对象，或者流式响应的生成器
    """
    # 生成会话ID
    session_id = str(uuid.uuid4())
    
    # 处理用户消息
    user_message = request.messages[-1]
    
    # 过滤敏感词
    filtered_content, sensitive_words = filter_sensitive_words(user_message.content)
    
    # 记录用户消息
    record_message(
        user_id=request.user_id,
        session_id=session_id,
        role="user",
        content=user_message.content,
        filtered_content=filtered_content,
        metadata={"sensitive_words": sensitive_words}
    )
    
    # 为用户消息附加知识库内容
    enhanced_query = attach_knowledge_to_query(filtered_content)
    
    # 准备发送给大模型的消息
    messages_for_llm = [msg.dict() for msg in request.messages[:-1]]
    messages_for_llm.append({
        "role": "user",
        "content": enhanced_query
    })
    
    # 调用大模型
    try:
        if stream or request.stream:
            # 流式响应
            return stream_chat_completion(
                request=request,
                session_id=session_id,
                messages=messages_for_llm
            )
        else:
            # 非流式响应
            return get_chat_completion(
                request=request,
                session_id=session_id,
                messages=messages_for_llm
            )
    except Exception as e:
        # 记录错误信息
        error_message = f"调用大模型失败: {str(e)}"
        print(error_message)
        
        # 生成错误响应
        error_response = Message(
            role="assistant",
            content="抱歉，我现在无法为您提供服务，请稍后再试。",
            metadata={"error": True}
        )
        
        # 记录错误响应
        record_message(
            user_id=request.user_id,
            session_id=session_id,
            role="assistant",
            content=error_response.content,
            metadata={"error": True, "error_message": str(e)}
        )
        
        return ChatResponse(
            user_id=request.user_id,
            message=error_response,
            model=request.model,
            usage=None
        )

def get_chat_completion(request: ChatRequest, session_id: str, messages: List[Dict[str, str]]) -> ChatResponse:
    """
    获取大模型的聊天完成响应
    """

    model_name = "Qwen/QwQ-32B"  # ✅ 使用硅基流动支持的模型名

    # 调用LiteLLM获取响应
    response = litellm.completion(
        # model=request.model,
        model=model_name,
        messages=messages,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        api_key="sk-uzwqzshzwyfjjrdhedyfpqpacibopopfqwpbogihnmdqxbue",
        api_base="https://api.siliconflow.cn/v1",
        custom_llm_provider="openai",  
        stream=False
    )
    
    # 提取响应内容
    response_content = response.choices[0].message.content
    
    # 过滤响应中的敏感词
    filtered_response, sensitive_words_in_response = filter_sensitive_words(response_content)
    
    # 创建响应消息
    response_message = Message(
        role="assistant",
        content=filtered_response,
        metadata={"sensitive_words": sensitive_words_in_response}
    )
    
    # 记录大模型响应
    record_message(
        user_id=request.user_id,
        session_id=session_id,
        role="assistant",
        content=response_content,
        filtered_content=filtered_response,
        metadata={"sensitive_words": sensitive_words_in_response}
    )
    
    # 提取使用情况统计
    usage = None
    if hasattr(response, "usage"):
        raw_usage = response.usage.to_dict() if hasattr(response.usage, "to_dict") else dict(response.usage)
        # 过滤usage字典，只保留整数类型的值
        usage = {}
        for key, value in raw_usage.items():
            # 跳过带有_details后缀的字段，它们可能是复杂类型
            if key.endswith('_details'):
                continue
            # 确保值是整数类型
            if isinstance(value, int):
                usage[key] = value
            elif value is not None:
                try:
                    usage[key] = int(value)
                except (ValueError, TypeError):
                    pass
    
    # 返回聊天响应
    return ChatResponse(
        user_id=request.user_id,
        message=response_message,
        model=request.model,
        usage=usage
    )

def stream_chat_completion(request: ChatRequest, session_id: str, messages: List[Dict[str, str]]) -> Generator[Dict[str, Any], None, None]:
    """
    获取大模型的流式聊天完成响应
    """
    # 调用LiteLLM获取流式响应
    response_stream = litellm.completion(
        model="Qwen/QwQ-32B",
        messages=messages,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        api_key="sk-uzwqzshzwyfjjrdhedyfpqpacibopopfqwpbogihnmdqxbue",
        api_base="https://api.siliconflow.cn/v1",
        custom_llm_provider="openai",  
        stream=True
    )
    
    full_response = ""
    
    # 处理流式响应
    for chunk in response_stream:
        if hasattr(chunk, "choices") and chunk.choices:
            choice = chunk.choices[0]
            if hasattr(choice, "delta") and hasattr(choice.delta, "content") and choice.delta.content:
                # 收集响应内容
                full_response += choice.delta.content
                
                # 过滤当前片段中的敏感词
                filtered_chunk, _ = filter_sensitive_words(choice.delta.content)
                
                # 生成流式响应
                yield {
                    "user_id": request.user_id,
                    "content": filtered_chunk,
                    "model": request.model,
                    "is_final": False
                }
    
    # 过滤完整响应中的敏感词
    filtered_full_response, sensitive_words_in_response = filter_sensitive_words(full_response)
    
    # 记录大模型响应
    record_message(
        user_id=request.user_id,
        session_id=session_id,
        role="assistant",
        content=full_response,
        filtered_content=filtered_full_response,
        metadata={"sensitive_words": sensitive_words_in_response}
    )
    
    # 生成最终响应
    yield {
        "user_id": request.user_id,
        "content": filtered_full_response,
        "model": request.model,
        "is_final": True,
        "metadata": {"sensitive_words": sensitive_words_in_response}
    }

def record_message(user_id: str, session_id: str, role: str, content: str, filtered_content: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
    """
    记录消息到数据库
    """
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 创建聊天历史记录
        chat_history = ChatHistory(
            user_id=user_id,
            session_id=session_id,
            role=role,
            content=content,
            filtered_content=filtered_content,
            message_metadata=metadata
        )
        
        # 添加到数据库
        db.add(chat_history)
        db.commit()
        db.refresh(chat_history)
    except Exception as e:
        # 发生错误时回滚
        db.rollback()
        print(f"记录消息失败: {str(e)}")
    finally:
        # 关闭数据库会话
        db.close()