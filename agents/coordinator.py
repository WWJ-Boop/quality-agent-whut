"""协调Agent

负责用户意图识别和Agent路由调度。
"""

from typing import Optional, Callable, Dict, List
from loguru import logger

from agents.base_agent import BaseAgent, AgentMessage
from agents.report_agent import ReportAnalysisAgent
from agents.standard_agent import StandardQAAgent
from agents.trend_agent import TrendAnalysisAgent


# 意图分类
INTENT_ANALYZE_REPORT = "analyze_report"
INTENT_STANDARD_QA = "standard_qa"
INTENT_TREND_ANALYSIS = "trend_analysis"
INTENT_GENERAL = "general"


class CoordinatorAgent(BaseAgent):
    """协调Agent

    职责:
    1. 接收用户输入
    2. 识别用户意图
    3. 将任务路由到对应的专业Agent
    4. 汇总结果返回给用户
    """

    def __init__(self, llm_caller: Optional[Callable] = None, vector_store=None):
        super().__init__(llm_caller)
        self.vector_store = vector_store
        self._sub_agents: Dict[str, BaseAgent] = {}
        self._init_sub_agents()

    def _init_sub_agents(self):
        """初始化子Agent"""
        self._sub_agents[INTENT_ANALYZE_REPORT] = ReportAnalysisAgent(
            llm_caller=self.llm_caller,
        )
        self._sub_agents[INTENT_STANDARD_QA] = StandardQAAgent(
            llm_caller=self.llm_caller,
            vector_store=self.vector_store,
        )
        self._sub_agents[INTENT_TREND_ANALYSIS] = TrendAnalysisAgent(
            llm_caller=self.llm_caller,
        )
        logger.info("协调Agent已初始化所有子Agent")

    @property
    def name(self) -> str:
        return "协调Agent"

    @property
    def description(self) -> str:
        return "智能路由Agent，根据用户意图分配任务到对应的专业Agent。"

    @property
    def system_prompt(self) -> str:
        return """你是"智检通"系统的协调调度Agent。你的职责是：

1. 分析用户输入的意图
2. 将任务路由到最合适的专业Agent
3. 如果用户意图不明确，主动询问确认

可用的专业Agent：
- {analyze_report}: 用于分析检测报告，提取指标，判定合格性
  触发词: 分析报告、检测报告、报告解读、合格判定、PDF分析
- {standard_qa}: 用于回答工程质量标准相关问题
  触发词: 标准、规范、条文、规定、GB、JGJ、合格标准、取样
- {trend_analysis}: 用于分析检测数据趋势
  触发词: 趋势、变化、统计、均值、波动、预警、图表

请根据用户输入判断最匹配的意图，返回对应的Agent名称。
如果用户输入涉及多个方面，选择最核心的意图。

只需返回Agent名称，不要添加其他内容。""".format(
            analyze_report=INTENT_ANALYZE_REPORT,
            standard_qa=INTENT_STANDARD_QA,
            trend_analysis=INTENT_TREND_ANALYSIS,
        )

    def _classify_intent(self, user_input: str) -> str:
        """分类用户意图"""
        # 基于关键词的快速分类
        keywords_report = ["报告", "分析", "检测", "PDF", "pdf", "合格", "不合格", "强度", "指标"]
        keywords_standard = ["标准", "规范", "条文", "规定", "GB", "gb", "JGJ", "jgj", "取样", "频率", "方法"]
        keywords_trend = ["趋势", "变化", "统计", "均值", "波动", "预警", "图表", "历史", "数据"]

        text = user_input.lower()

        report_score = sum(1 for k in keywords_report if k in text)
        standard_score = sum(1 for k in keywords_standard if k in text)
        trend_score = sum(1 for k in keywords_trend if k in text)

        max_score = max(report_score, standard_score, trend_score)

        if max_score == 0:
            # 无法通过关键词判断，使用LLM
            return self._llm_classify_intent(user_input)

        if report_score == max_score:
            return INTENT_ANALYZE_REPORT
        elif standard_score == max_score:
            return INTENT_STANDARD_QA
        else:
            return INTENT_TREND_ANALYSIS

    def _llm_classify_intent(self, user_input: str) -> str:
        """使用LLM分类意图"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"请判断以下输入的意图:\n{user_input}"},
        ]
        response = self.call_llm(messages).strip()

        # 从响应中提取意图
        for intent in [INTENT_ANALYZE_REPORT, INTENT_STANDARD_QA, INTENT_TREND_ANALYSIS]:
            if intent in response:
                return intent

        return INTENT_GENERAL

    def run(self, user_input: str, context: str = "", **kwargs) -> str:
        """执行协调调度"""
        logger.info(f"[{self.name}] 收到用户输入: {user_input[:50]}...")

        # 分类意图
        intent = self._classify_intent(user_input)
        logger.info(f"[{self.name}] 意图识别结果: {intent}")

        # 路由到子Agent
        if intent in self._sub_agents:
            agent = self._sub_agents[intent]
            logger.info(f"[{self.name}] 路由到: {agent.name}")
            return agent.run(user_input, context=context, **kwargs)

        # 通用回复
        return self._general_response(user_input, context)

    def _general_response(self, user_input: str, context: str = "") -> str:
        """通用回复"""
        messages = [
            {"role": "system", "content": """你是"智检通"工程质量检测分析智能体系统的助手。
你可以帮助用户：
1. 分析工程质量检测报告
2. 查询工程质量标准规范
3. 分析检测数据趋势

请引导用户明确需求，或直接回答用户的一般性问题。"""},
            {"role": "user", "content": user_input},
        ]
        return self.call_llm(messages)
