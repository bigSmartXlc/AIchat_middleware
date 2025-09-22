import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

# 创建FastAPI应用
app = FastAPI(title="智能客服中间件", description="使用LiteLLM的智能客服中间件系统")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入路由
from api import chat_router

# 注册路由
app.include_router(chat_router.router, prefix="/api", tags=["聊天服务"])

@app.get("/")
def read_root():
    """根路径，返回服务状态"""
    return {"status": "running", "version": "1.0.0"}

if __name__ == "__main__":
    # 启动服务器
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True
    )