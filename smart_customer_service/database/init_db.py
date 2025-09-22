import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# 获取数据库URL
database_url = os.getenv("DATABASE_URL", "sqlite:///./chat_history.db")

# 创建数据库引擎
engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
)

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
def init_database():
    """初始化数据库，创建所有表"""
    try:
        # 创建数据库表
        Base.metadata.create_all(bind=engine)
        print("数据库初始化成功！")
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")

if __name__ == "__main__":
    init_database()