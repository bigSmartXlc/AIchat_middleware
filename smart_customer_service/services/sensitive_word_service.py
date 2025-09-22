import re
from typing import List, Tuple, Dict, Any

class SensitiveWordFilter:
    """敏感词过滤服务类"""
    
    def __init__(self):
        """初始化敏感词过滤器，加载敏感词库"""
        # 初始化敏感词库，可以从文件或数据库加载
        self.sensitive_words = self._load_sensitive_words()
        # 构建DFA（Deterministic Finite Automaton）敏感词检测算法
        self.dfa = self._build_dfa()
        
    def _load_sensitive_words(self) -> List[str]:
        """加载敏感词库，实际应用中可以从文件或数据库加载"""
        # 这里使用简单的敏感词列表作为示例
        return [
            "敏感词1", "敏感词2", "敏感词3", "政治", "暴力", 
            "色情", "赌博", "毒品", "诈骗", "恶意"
        ]
        
    def _build_dfa(self) -> Dict[str, Any]:
        """构建DFA敏感词检测算法"""
        dfa = {}
        for word in self.sensitive_words:
            current = dfa
            for char in word:
                if char not in current:
                    current[char] = {}
                current = current[char]
            current["is_end"] = True
        return dfa
        
    def filter_sensitive_words(self, text: str) -> Tuple[str, List[str]]:
        """
        过滤文本中的敏感词
        
        参数:
            text: 需要过滤的文本
        
        返回:
            Tuple[str, List[str]]: (过滤后的文本, 检测到的敏感词列表)
        """
        if not text or not self.dfa:
            return text, []
            
        result = list(text)
        sensitive_words_found = []
        
        for i in range(len(result)):
            current = self.dfa
            matched = False
            word = ""
            
            for j in range(i, len(result)):
                char = result[j]
                if char in current:
                    current = current[char]
                    word += char
                    if "is_end" in current:
                        sensitive_words_found.append(word)
                        # 替换敏感词为*号
                        for k in range(i, j + 1):
                            result[k] = "*"
                        matched = True
                        break
                else:
                    break
            
            if matched:
                # 跳过已处理的字符
                i += len(word) - 1
                
        return "".join(result), list(set(sensitive_words_found))

# 创建全局的敏感词过滤器实例
sensitive_word_filter = SensitiveWordFilter()

# 提供便捷的过滤函数
def filter_sensitive_words(text: str) -> Tuple[str, List[str]]:
    """便捷函数，调用敏感词过滤器进行敏感词过滤"""
    return sensitive_word_filter.filter_sensitive_words(text)