# 智能客服中间件系统

基于 LiteLLM 的智能客服中间件系统，支持敏感词过滤、消息记录到数据库以及知识库集成功能。

## 功能特点

- **大模型集成**：使用 LiteLLM 统一调用多种大语言模型（如 OpenAI、Anthropic 等）
- **敏感词过滤**：基于 DFA 算法的敏感词检测和替换
- **消息记录**：自动将用户消息和大模型响应记录到数据库
- **知识库集成**：为用户消息附加公司知识库内容，提升回答质量
- **流式响应**：支持大模型的流式输出，提供更好的用户体验
- **聊天历史管理**：支持查询和管理用户的聊天历史记录

## 目录结构

```
smart_customer_service/
├── .env                    # 环境配置文件
├── main.py                 # 主应用程序入口
├── requirements.txt        # 项目依赖
├── api/                    # API路由模块
│   └── chat_router.py      # 聊天相关API路由
├── services/               # 业务服务模块
│   ├── chat_service.py     # 聊天服务（核心功能）
│   ├── sensitive_word_service.py  # 敏感词过滤服务
│   ├── knowledge_base_service.py  # 知识库服务
│   └── chat_history_service.py    # 聊天历史服务
├── database/               # 数据库模块
│   ├── database.py         # 数据库配置
│   └── init_db.py          # 数据库初始化脚本
├── models/                 # 数据模型模块
│   └── chat_models.py      # 聊天相关数据模型
├── knowledge_base.json     # 知识库数据文件
└── test_client.py          # 测试客户端
```

## 环境要求

- Python 3.8+
- pip 20.0+

## 安装步骤

1. 克隆项目代码到本地

2. 安装依赖包

   ```bash
   pip install -r requirements.txt
   # 或使用国内镜像加速
   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
   ```

3. 初始化数据库
   ```bash
   python database/init_db.py
   ```

## 配置说明

编辑`.env`文件，配置以下参数：

```env
# 数据库配置
DATABASE_URL=sqlite:///./chat_history.db

# 大模型API配置
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# 服务配置
HOST=0.0.0.0
PORT=8000

# 日志级别
LOG_LEVEL=INFO
```

## 启动方法

```bash
python main.py
```

服务将在指定的主机和端口上启动（默认为 0.0.0.0:8000）。

## API 接口说明

### 1. 发送普通消息

- **URL**: `/api/chat`
- **方法**: POST
- **请求体**:
  ```json
  {
    "user_id": "用户ID",
    "messages": [
      {
        "role": "user",
        "content": "用户消息内容"
      }
    ],
    "model": "Qwen/QwQ-32B",
    "max_tokens": 1000,
    "temperature": 0.7,
    "stream": false
  }
  ```
- **响应**:
  ```json
  {
    "user_id": "用户ID",
    "message": {
      "role": "assistant",
      "content": "大模型响应内容",
      "timestamp": "时间戳",
      "metadata": { "sensitive_words": [] }
    },
    "model": "Qwen/QwQ-32B",
    "usage": {
      "prompt_tokens": 10,
      "completion_tokens": 50,
      "total_tokens": 60
    },
    "timestamp": "时间戳"
  }
  ```

### 2. 发送流式消息

- **URL**: `/api/chat/stream`
- **方法**: POST
- **请求体**: 同普通消息
- **响应**: SSE (Server-Sent Events) 格式的流式响应

### 3. 获取聊天历史

- **URL**: `/api/history/{user_id}`
- **方法**: GET
- **响应**:
  ```json
  {
    "history": [
      {
        "id": 1,
        "user_id": "用户ID",
        "session_id": "会话ID",
        "role": "user",
        "content": "消息内容",
        "filtered_content": "过滤后内容",
        "timestamp": "时间戳",
        "metadata": { "sensitive_words": [] }
      }
    ]
  }
  ```

## 测试方法

使用提供的测试客户端进行功能测试：

```bash
python test_client.py
```

然后根据提示取消注释相应的测试函数调用，执行具体的测试。

## 知识库管理

知识库内容存储在`knowledge_base.json`文件中，您可以根据需要编辑和扩展这个文件。格式如下：

```json
[
  {
    "id": "kb001",
    "title": "知识标题",
    "content": "知识内容"
  }
]
```

## 敏感词管理

敏感词列表在`services/sensitive_word_service.py`文件中的`_load_sensitive_words`方法中定义。在实际应用中，您可以从文件或数据库加载敏感词库。

## 注意事项

1. 在生产环境中，请确保 API 密钥的安全存储，不要将敏感信息硬编码在代码中。
2. 默认使用 SQLite 数据库，在生产环境中建议切换到 MySQL 或 PostgreSQL 等更适合生产环境的数据库。
3. 对于大规模应用，建议进一步优化敏感词过滤算法和知识库检索算法，以提高性能。
4. 如需支持更多大模型，请参考 LiteLLM 的官方文档进行配置。
