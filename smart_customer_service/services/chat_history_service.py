from typing import List, Dict, Any, Optional
from datetime import datetime
from database.database import get_db, ChatHistory

class ChatHistoryService:
    """聊天历史服务类，用于管理和获取用户的聊天历史记录"""
    
    def get_user_chat_history(self, user_id: str, session_id: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取用户的聊天历史记录
        
        参数:
            user_id: 用户ID
            session_id: 会话ID，可选，如果提供则只返回该会话的记录
            limit: 返回的最大记录数
            offset: 偏移量，用于分页
        
        返回:
            List[Dict[str, Any]]: 聊天历史记录列表
        """
        # 获取数据库会话
        db = next(get_db())
        
        try:
            # 构建查询
            query = db.query(ChatHistory).filter(ChatHistory.user_id == user_id)
            
            # 如果指定了会话ID，则过滤会话
            if session_id:
                query = query.filter(ChatHistory.session_id == session_id)
            
            # 按时间戳降序排列，并应用分页
            chat_history = query.order_by(ChatHistory.timestamp.desc()).offset(offset).limit(limit).all()
            
            # 转换为字典列表
            result = []
            for record in chat_history:
                result.append({
                    "id": record.id,
                    "user_id": record.user_id,
                    "session_id": record.session_id,
                    "role": record.role,
                    "content": record.content,
                    "filtered_content": record.filtered_content,
                    "timestamp": record.timestamp.isoformat() if record.timestamp else None,
                    "metadata": record.message_metadata
                })
            
            return result
        except Exception as e:
            print(f"获取聊天历史记录失败: {str(e)}")
            return []
        finally:
            # 关闭数据库会话
            db.close()
            
    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        获取用户的所有会话列表
        
        参数:
            user_id: 用户ID
        
        返回:
            List[Dict[str, Any]]: 会话列表，包含会话ID和最近消息时间
        """
        # 获取数据库会话
        db = next(get_db())
        
        try:
            # 查询用户的所有会话ID和最近消息时间
            # 注意：SQLAlchemy的查询方式可能因版本而异，这里使用了基本的查询方式
            from sqlalchemy import func
            
            # 按会话分组，获取每个会话的最大时间戳
            sessions_query = (
                db.query(
                    ChatHistory.session_id,
                    func.max(ChatHistory.timestamp).label("latest_message_time")
                )
                .filter(ChatHistory.user_id == user_id)
                .group_by(ChatHistory.session_id)
                .order_by(func.max(ChatHistory.timestamp).desc())
                .all()
            )
            
            # 转换为字典列表
            result = []
            for session in sessions_query:
                result.append({
                    "session_id": session.session_id,
                    "latest_message_time": session.latest_message_time.isoformat() if session.latest_message_time else None
                })
            
            return result
        except Exception as e:
            print(f"获取用户会话列表失败: {str(e)}")
            return []
        finally:
            # 关闭数据库会话
            db.close()
            
    def delete_chat_history(self, history_id: int = None, user_id: str = None, session_id: str = None) -> bool:
        """
        删除聊天历史记录
        
        参数:
            history_id: 历史记录ID，可选
            user_id: 用户ID，可选，如果提供则删除该用户的所有记录
            session_id: 会话ID，可选，如果提供则删除该会话的所有记录
        
        返回:
            bool: 删除是否成功
        """
        # 至少需要提供一个参数
        if not history_id and not user_id and not session_id:
            return False
            
        # 获取数据库会话
        db = next(get_db())
        
        try:
            # 构建查询
            query = db.query(ChatHistory)
            
            # 应用过滤条件
            if history_id:
                query = query.filter(ChatHistory.id == history_id)
            if user_id:
                query = query.filter(ChatHistory.user_id == user_id)
            if session_id:
                query = query.filter(ChatHistory.session_id == session_id)
            
            # 执行删除
            deleted_count = query.delete(synchronize_session=False)
            db.commit()
            
            return deleted_count > 0
        except Exception as e:
            # 发生错误时回滚
            db.rollback()
            print(f"删除聊天历史记录失败: {str(e)}")
            return False
        finally:
            # 关闭数据库会话
            db.close()

# 创建全局的聊天历史服务实例
chat_history_service = ChatHistoryService()

# 提供便捷的函数
def get_user_chat_history(user_id: str, session_id: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """便捷函数，获取用户的聊天历史记录"""
    return chat_history_service.get_user_chat_history(user_id, session_id, limit, offset)
    
def get_user_sessions(user_id: str) -> List[Dict[str, Any]]:
    """便捷函数，获取用户的所有会话列表"""
    return chat_history_service.get_user_sessions(user_id)
    
def delete_chat_history(history_id: int = None, user_id: str = None, session_id: str = None) -> bool:
    """便捷函数，删除聊天历史记录"""
    return chat_history_service.delete_chat_history(history_id, user_id, session_id)