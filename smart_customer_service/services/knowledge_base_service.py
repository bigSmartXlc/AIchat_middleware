import os
import json
from typing import List, Dict, Any, Optional
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class KnowledgeBaseService:
    """知识库服务类，用于管理和检索公司知识库"""
    
    def __init__(self):
        """初始化知识库服务"""
        # 加载知识库数据
        self.knowledge_base = self._load_knowledge_base()
        # 初始化向量izer和文档向量
        self.vectorizer = None
        self.document_vectors = None
        self._prepare_knowledge_base()
        
    def _load_knowledge_base(self) -> List[Dict[str, str]]:
        """加载知识库数据，实际应用中可以从文件、数据库或API加载"""
        # 这里使用简单的知识库示例
        knowledge_base = [
            {
                "id": "kb001",
                "title": "公司简介",
                "content": "我公司成立于2000年，是一家专注于人工智能技术研发的高科技企业，总部位于北京。"
            },
            {
                "id": "kb002",
                "title": "产品介绍",
                "content": "我们的主要产品包括智能客服系统、自然语言处理平台和机器学习工具等。"
            },
            {
                "id": "kb003",
                "title": "服务条款",
                "content": "我们提供7×24小时客户服务，支持在线咨询、电话咨询和邮件咨询等多种方式。"
            },
            {
                "id": "kb004",
                "title": "常见问题",
                "content": "如何申请使用我们的产品？您可以通过官网注册账号，或联系销售团队获取详细信息。"
            }
        ]
        
        # 检查是否存在知识库文件
        kb_file = "d:\workTool\code\llm\smart_customer_service\knowledge_base.json"
        if os.path.exists(kb_file):
            try:
                with open(kb_file, 'r', encoding='utf-8') as f:
                    knowledge_base = json.load(f)
            except Exception as e:
                print(f"加载知识库文件失败: {e}")
        
        return knowledge_base
        
    def _prepare_knowledge_base(self):
        """准备知识库，构建文本向量用于相似度计算"""
        if not self.knowledge_base:
            return
            
        # 提取文档内容
        documents = [item["content"] for item in self.knowledge_base]
        
        # 初始化TF-IDF向量izer
        self.vectorizer = TfidfVectorizer(
            token_pattern=r'(?u)\b\w+\b',
            stop_words=None,  # 中文可以考虑使用自定义停用词表
            max_df=0.8,
            min_df=1
        )
        
        # 计算文档向量
        self.document_vectors = self.vectorizer.fit_transform(documents)
        
    def search_knowledge_base(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        """
        根据查询从知识库中检索相关信息
        
        参数:
            query: 用户查询
            top_k: 返回的最相关文档数量
        
        返回:
            List[Dict[str, str]]: 检索到的相关知识库条目
        """
        if not self.knowledge_base or self.document_vectors is None:
            return []
            
        # 将查询转换为向量
        query_vector = self.vectorizer.transform([query])
        
        # 计算相似度
        similarities = cosine_similarity(query_vector, self.document_vectors).flatten()
        
        # 获取最相似的top_k个文档索引
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        # 返回最相关的文档
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # 设置阈值，只返回相似度足够高的结果
                results.append({
                    "id": self.knowledge_base[idx]["id"],
                    "title": self.knowledge_base[idx]["title"],
                    "content": self.knowledge_base[idx]["content"],
                    "similarity": float(similarities[idx])
                })
        
        return results
        
    def add_knowledge_to_query(self, query: str, knowledge: List[Dict[str, str]]) -> str:
        """
        将知识库内容添加到用户查询中
        
        参数:
            query: 用户原始查询
            knowledge: 从知识库中检索到的相关信息
        
        返回:
            str: 添加了知识库内容的查询
        """
        if not knowledge:
            return query
            
        # 构建上下文提示
        context = "\n".join([f"[{item['title']}]{item['content']}" for item in knowledge])
        
        # 构建新的查询，包含知识库上下文
        new_query = f"用户问题：{query}\n\n请参考以下知识库内容回答用户问题：\n{context}\n\n请基于知识库内容回答，不要编造信息。"
        
        return new_query

# 创建全局的知识库服务实例
knowledge_base_service = KnowledgeBaseService()

# 提供便捷的函数
def search_knowledge(query: str, top_k: int = 3) -> List[Dict[str, str]]:
    """便捷函数，从知识库中检索相关信息"""
    return knowledge_base_service.search_knowledge_base(query, top_k)
    
def attach_knowledge_to_query(query: str, top_k: int = 3) -> str:
    """便捷函数，为用户查询附加知识库内容"""
    # 从知识库中检索相关信息
    knowledge = knowledge_base_service.search_knowledge_base(query, top_k)
    # 将知识库内容添加到查询中
    return knowledge_base_service.add_knowledge_to_query(query, knowledge)