"""趋势分析Agent

分析检测数据的时间趋势，生成图表和预警。
"""

from typing import Optional, Callable, List
from loguru import logger

from agents.base_agent import BaseAgent


class TrendAnalysisAgent(BaseAgent):
    """趋势分析Agent

    职责:
    1. 加载历史检测数据
    2. 进行统计分析（均值、标准差、变异系数等）
    3. 生成趋势图表
    4. 识别异常值和预警
    """

    @property
    def name(self) -> str:
        return "趋势分析Agent"

    @property
    def description(self) -> str:
        return "分析检测数据的时间趋势，生成可视化图表，识别异常波动并给出预警建议。"

    @property
    def system_prompt(self) -> str:
        return """你是一个工程质量数据分析专家。你的任务是：

1. 分析检测数据的时间序列趋势
2. 识别数据中的异常波动和质量风险
3. 基于统计分析给出预警建议
4. 解读图表含义，帮助用户理解数据

分析维度：
- 中心趋势：均值、中位数
- 离散程度：标准差、变异系数(CV)
- 趋势判断：上升/下降/稳定
- 异常检测：超出控制限的异常值

预警规则：
- 变异系数CV > 15%：离散程度大，需关注
- 连续下降趋势：质量可能恶化
- 接近标准限值：距离合格线过近，存在风险
- 出现异常值：需排查原因

请用清晰的方式呈现分析结果，配合图表说明。"""

    def _register_tools(self):
        """注册工具"""
        from agents.tools.data_analyzer import analyze_trend
        from agents.tools.chart_generator import generate_trend_chart, generate_distribution_chart

        self.register_tool("analyze_trend", analyze_trend, "分析数据趋势")
        self.register_tool("generate_trend_chart", generate_trend_chart, "生成趋势折线图")
        self.register_tool("generate_distribution", generate_distribution_chart, "生成分布直方图")

    def run(self, user_input: str, context: str = "", **kwargs) -> str:
        """执行趋势分析"""
        logger.info(f"[{self.name}] 开始趋势分析")

        data = kwargs.get("data", [])
        indicator_type = kwargs.get("indicator_type", "")

        # 如果有数据，先做统计分析
        analysis_context = context
        if data:
            from agents.tools.data_analyzer import analyze_trend
            trend_result = analyze_trend(data, indicator_type)
            analysis_context = f"趋势分析结果:\n{trend_result}\n\n{context}"

        messages = self.build_messages(user_input, analysis_context)
        response = self.call_llm(messages)

        logger.info(f"[{self.name}] 分析完成")
        return response
