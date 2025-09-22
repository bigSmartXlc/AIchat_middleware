from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class Message(BaseModel):
    """消息模型，用于表示聊天消息"""
    role: str = Field(..., description="消息角色，如user或assistant")
    content: str = Field(..., description="消息内容")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="消息时间戳")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="消息元数据")

class ChatRequest(BaseModel):
    """聊天请求模型，用于接收客户端的聊天请求"""
    user_id: str = Field(..., description="用户ID")
    messages: List[Message] = Field(..., description="聊天消息列表")
    model: str = Field(default="Qwen/QwQ-32B", description="使用的大模型")
    max_tokens: Optional[int] = Field(default=1000, description="最大生成token数")
    temperature: Optional[float] = Field(default=0.7, description="生成温度")
    stream: Optional[bool] = Field(default=False, description="是否使用流式响应")
    additional_context: Optional[Dict[str, Any]] = Field(default=None, description="额外上下文信息")

class ChatResponse(BaseModel):
    """聊天响应模型，用于返回大模型的响应"""
    user_id: str = Field(..., description="用户ID")
    message: Message = Field(..., description="响应消息")
    model: str = Field(..., description="使用的大模型")
    usage: Optional[Dict[str, int]] = Field(default=None, description="token使用情况")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")

class ChatHistoryModel(BaseModel):
    """聊天历史模型，用于表示数据库中的聊天历史记录"""
    id: Optional[int] = Field(default=None, description="记录ID")
    user_id: str = Field(..., description="用户ID")
    session_id: str = Field(..., description="会话ID")
    role: str = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")
    filtered_content: Optional[str] = Field(default=None, description="过滤后的消息内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="消息时间戳")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="消息元数据")