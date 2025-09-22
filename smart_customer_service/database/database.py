import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# 加载环境变量
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chat_history.db")

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# 创建会话本地类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

class ChatHistory(Base):
    """聊天历史数据库模型"""
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True)
    session_id = Column(String(50), index=True)
    role = Column(String(20))
    content = Column(Text)
    filtered_content = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)
    message_metadata = Column(JSON, nullable=True)

# 初始化数据库
def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)

# 获取数据库会话
def get_db():
    """获取数据库会话的依赖项"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()