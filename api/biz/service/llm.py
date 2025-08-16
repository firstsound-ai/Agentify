from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from typing import AsyncIterable
from common.utils.get_llm_model import get_llm_model


model_kwargs = {
    "base_url": "https://api.siliconflow.cn/v1",
    "api_key": "sk-dyeoanatkugzcldlztzvybznubiueuhieiopgytuycztryqe",
}

llm = get_llm_model(model_name="Qwen/Qwen3-30B-A3B-Instruct-2507", temperature=0.5, model_kwargs=model_kwargs)

class LLMBIZ:
    @staticmethod
    async def stream_llm_response(prompt: str) -> AsyncIterable[str]:
        """流式调用 LLM（示例使用 OpenAI）"""
        # 转换为异步迭代器
        async for chunk in llm.astream([HumanMessage(content=prompt)]):
            if hasattr(chunk, 'content'):  # 确保chunk有content属性
                yield chunk.content
