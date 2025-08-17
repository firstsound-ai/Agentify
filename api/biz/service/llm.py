from langchain.schema import HumanMessage
from typing import AsyncIterable
from common.utils.get_llm_model import get_llm_model

llm = get_llm_model(model_name="gemini-2.5-flash", temperature=0.5)


class LLMBIZ:
    @staticmethod
    async def stream_llm_response(prompt: str) -> AsyncIterable[str]:
        """流式调用 LLM（示例使用 OpenAI）"""
        # 转换为异步迭代器
        async for chunk in llm.astream([HumanMessage(content=prompt)]):
            if hasattr(chunk, "content"):  # 确保chunk有content属性
                yield chunk.content
