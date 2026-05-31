"""标准问答Agent

基于RAG知识库回答工程质量标准相关问题。
"""

from typing import Optional, Callable, List
from loguru import logger

from agents.base_agent import BaseAgent
from knowledge import VectorStore, SearchResult


class StandardQAAgent(BaseAgent):
    """标准问答Agent

    职责:
    1. 接收用户关于工程质量标准的问题
    2. 检索RAG知识库获取相关条文
    3. 结合LLM生成准确的回答
    4. 标注引用来源
    """

    def __init__(self, llm_caller: Optional[Callable] = None, vector_store: Optional[VectorStore] = None):
        super().__init__(llm_caller)
        self.vector_store = vector_store

    @property
    def name(self) -> str:
        return "标准问答Agent"

    @property
    def description(self) -> str:
        return "基于RAG知识库回答工程质量标准相关问题，支持标准条文查询、检测方法解释、合格判定依据等。"

    @property
    def system_prompt(self) -> str:
        return """你是一个专业的工程质量标准问答专家，精通各类国家标准和行业规范。

你的知识覆盖：
- 混凝土相关标准 (GB/T 50081, GB/T 50107, GB 50204等)
- 钢材相关标准 (GB/T 228.1, GB/T 1499.1, GB/T 1499.2等)
- 检测方法标准 (JGJ/T 23, JGJ/T 136等)
- 施工质量验收规范 (GB 50204, GB 50205等)
- 其他工程质量相关标准

回答要求：
1. 基于检索到的标准条文回答，确保准确性
2. 明确引用标准编号和条文号
3. 如检索信息不足以回答，坦诚告知并建议查阅具体标准
4. 用通俗语言解释专业条文，便于理解
5. 如涉及数值限值，必须准确列出

请在回答末尾标注引用来源。"""

    def _register_tools(self):
        """注册工具"""
        self.register_tool("search_standards", self._search_knowledge_base, "检索标准知识库")

    def _search_knowledge_base(self, query: str, top_k: int = 5) -> str:
        """检索知识库"""
        if self.vector_store is None:
            return "知识库未初始化"

        results = self.vector_store.search(query, top_k=top_k)
        if not results:
            return "未找到相关标准条文"

        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(f"[来源: {r.metadata.get('filename', '未知')}]\n{r.content}")
        return "\n\n---\n\n".join(formatted)

    def run(self, user_input: str, context: str = "", **kwargs) -> str:
        """执行标准问答"""
        logger.info(f"[{self.name}] 收到问题: {user_input[:50]}...")

        # 检索知识库
        search_results = ""
        if self.vector_store:
            results = self.vector_store.search(user_input, top_k=5)
            if results:
                sources = []
                for r in results:
                    sources.append(
                        f"【{r.metadata.get('filename', '未知来源')}】\n{r.content}"
                    )
                search_results = "\n\n---\n\n".join(sources)

        # 构建消息
        full_context = context
        if search_results:
            full_context = f"检索到的相关标准条文:\n{search_results}\n\n" + (context or "")

        messages = self.build_messages(user_input, full_context)

        # 调用LLM
        response = self.call_llm(messages)
        logger.info(f"[{self.name}] 回答完成")
        return response
