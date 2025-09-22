from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from models.chat_models import ChatRequest, Message, ChatResponse
from services.chat_service import process_chat_request, record_message
from services.sensitive_word_service import filter_sensitive_words

# 创建路由
router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """处理客户端的聊天请求"""
    try:
        # 处理聊天请求
        response = process_chat_request(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
def stream_chat_endpoint(request: ChatRequest):
    """处理客户端的流式聊天请求"""
    try:
        # 生成流式响应生成器
        def generate():
            for chunk in process_chat_request(request, stream=True):
                if isinstance(chunk, dict):
                    yield f"data: {chunk}\n\n"
                else:
                    yield f"data: {chunk.model_dump_json()}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{user_id}")
def get_chat_history(user_id: str):
    """获取用户的聊天历史记录"""
    try:
        from services.chat_history_service import get_user_chat_history
        history = get_user_chat_history(user_id)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))