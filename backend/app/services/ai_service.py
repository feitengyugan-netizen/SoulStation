"""
AI 服务 - 基于豆包 API
"""
import os
import httpx
from openai import OpenAI
from app.core.config import settings


class AIService:
    """AI 服务类"""

    def __init__(self):
        """初始化 AI 客户端"""
        # 创建httpx客户端，避免proxies参数问题
        http_client = httpx.Client(
            timeout=60.0,
            limits=httpx.Limits(max_keepalive_connections=50, max_connections=100)
        )

        self.client = OpenAI(
            base_url=settings.DOUBAO_BASE_URL,
            api_key=settings.DOUBAO_API_KEY,
            http_client=http_client
        )
        self.model = settings.DOUBAO_MODEL

    def chat(
        self,
        messages: list,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        发起聊天请求

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            stream: 是否流式返回
            temperature: 温度参数（0-1），越高越随机
            max_tokens: 最大 token 数

        Returns:
            str: AI 的回复内容
        """
        try:
            if stream:
                # 流式返回
                response = ""
                stream_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=True,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                for chunk in stream_response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        response += chunk.choices[0].delta.content
                return response
            else:
                # 非流式返回
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=False,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return completion.choices[0].message.content

        except Exception as e:
            raise Exception(f"AI 服务调用失败: {str(e)}")

    def generate_system_prompt(self, context: str = "") -> str:
        """
        生成系统提示词

        Args:
            context: 上下文信息（可选）

        Returns:
            str: 系统提示词
        """
        base_prompt = """你是 SoulStation 心理咨询平台的智能助手，名叫"小宁"。你的职责是：

1. **专业角色**：你是一个温暖、专业、有同理心的心理健康咨询助手
2. **服务宗旨**：为用户提供心理支持、情感疏导和心理健康知识普及
3. **交流风格**：
   - 语气温和、友善，不带评判色彩
   - 善于倾听，给予积极回应
   - 使用通俗易懂的语言，避免过于专业的术语
   - 适当使用鼓励和支持性的话语

4. **能力范围**：
   - 提供心理健康知识科普
   - 给出情感支持和疏导建议
   - 推荐合适的心理测试或咨询师
   - 引导用户表达情感和困惑

5. **注意事项**：
   - 不要给出明确的医学诊断
   - 遇到严重心理危机（如自伤倾向），建议立即寻求专业帮助
   - 保持客观中立，不替用户做决定
   - 回复要简洁明了，通常不超过200字

6. **回复格式**：
   - 适当使用表情符号，让对话更亲切（如 💚 ✨ 🌟）
   - 重点内容可以用加粗或列表呈现
   - 每次回复包含1-2个要点即可"""

        if context:
            return f"{base_prompt}\n\n**当前对话上下文**：\n{context}"
        return base_prompt


# 创建全局 AI 服务实例
ai_service = AIService()
