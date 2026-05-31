"""Agent基类

所有专项Agent的基类，提供统一的接口和通用能力。
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class AgentMessage:
    """Agent消息"""
    role: str  # "user" | "assistant" | "system" | "tool"
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class ToolResult:
    """工具调用结果"""
    tool_name: str
    result: str
    success: bool = True
    error: Optional[str] = None


class BaseAgent(ABC):
    """Agent基类

    所有Agent需实现:
    - name: Agent名称
    - description: Agent描述
    - system_prompt: 系统提示词
    - tools: 可用工具列表
    - run(): 执行推理
    """

    def __init__(self, llm_caller: Optional[Callable] = None):
        """
        Args:
            llm_caller: LLM调用函数，签名 (messages: list) -> str
        """
        self.llm_caller = llm_caller
        self._tools: Dict[str, Callable] = {}
        self._register_tools()

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent名称"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Agent描述，用于协调Agent的路由决策"""
        pass

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """系统提示词"""
        pass

    def _register_tools(self):
        """注册Agent工具，子类可重写"""
        pass

    def register_tool(self, name: str, func: Callable, description: str = ""):
        """注册一个工具"""
        self._tools[name] = func
        logger.debug(f"[{self.name}] 注册工具: {name}")

    def get_tools_description(self) -> str:
        """获取所有工具的描述，用于提示词"""
        if not self._tools:
            return "无可用工具"
        lines = []
        for name, func in self._tools.items():
            doc = func.__doc__ or "无描述"
            lines.append(f"- {name}: {doc.strip()}")
        return "\n".join(lines)

    def call_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """调用工具"""
        if tool_name not in self._tools:
            return ToolResult(
                tool_name=tool_name,
                result="",
                success=False,
                error=f"工具 {tool_name} 不存在",
            )
        try:
            result = self._tools[tool_name](**kwargs)
            return ToolResult(tool_name=tool_name, result=str(result), success=True)
        except Exception as e:
            logger.error(f"[{self.name}] 工具 {tool_name} 调用失败: {e}")
            return ToolResult(tool_name=tool_name, result="", success=False, error=str(e))

    def call_llm(self, messages: List[Dict[str, str]]) -> str:
        """调用LLM"""
        if self.llm_caller is None:
            raise RuntimeError("LLM调用函数未设置")
        return self.llm_caller(messages)

    def build_messages(self, user_input: str, context: str = "") -> List[Dict[str, str]]:
        """构建消息列表"""
        messages = [{"role": "system", "content": self.system_prompt}]
        if context:
            messages.append({"role": "system", "content": f"参考信息:\n{context}"})
        messages.append({"role": "user", "content": user_input})
        return messages

    @abstractmethod
    def run(self, user_input: str, context: str = "", **kwargs) -> str:
        """执行Agent推理，返回结果文本"""
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name}>"
