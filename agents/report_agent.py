"""报告分析Agent

解析工程质量检测报告，提取关键指标并判定合格性。
"""

from typing import Optional, Callable
from loguru import logger

from agents.base_agent import BaseAgent


class ReportAnalysisAgent(BaseAgent):
    """报告分析Agent

    职责:
    1. 解析上传的检测报告PDF/Excel
    2. 提取关键检测指标
    3. 对照标准进行合格性判定
    4. 生成分析结论
    """

    @property
    def name(self) -> str:
        return "报告分析Agent"

    @property
    def description(self) -> str:
        return "解析工程质量检测报告PDF/Excel，提取关键指标数据，对照标准判定合格性，生成分析结论。"

    @property
    def system_prompt(self) -> str:
        return """你是一个专业的工程质量检测报告分析专家。你的任务是：

1. 解析用户上传的检测报告内容
2. 提取报告中的关键检测指标（如混凝土强度、钢筋性能、坍落度等）
3. 对照相关国家标准判定各项指标是否合格
4. 生成清晰、专业的分析结论

分析要求：
- 使用专业术语，保持准确性
- 对每个指标给出明确的合格/不合格判定
- 指出可能的质量风险和建议
- 引用具体的标准条文作为判定依据

可参考的标准：
- GB/T 50107 混凝土强度检验评定标准
- GB 50204 混凝土结构工程施工质量验收规范
- GB/T 228.1 金属材料拉伸试验
- GB/T 1499.2 钢筋混凝土用钢 第2部分：热轧带肋钢筋
- JGJ/T 23 回弹法检测混凝土抗压强度技术规程

请用专业但易懂的方式回答，确保非专业人士也能理解关键结论。"""

    def _register_tools(self):
        """注册工具"""
        from agents.tools.pdf_parser import parse_report_pdf, extract_indicators
        from agents.tools.data_analyzer import check_compliance, batch_check_compliance

        self.register_tool("parse_report_pdf", parse_report_pdf, "解析PDF检测报告")
        self.register_tool("extract_indicators", extract_indicators, "提取检测指标")
        self.register_tool("check_compliance", check_compliance, "检查单个指标合格性")
        self.register_tool("batch_check", batch_check_compliance, "批量检查指标合格性")

    def run(self, user_input: str, context: str = "", **kwargs) -> str:
        """执行报告分析

        Args:
            user_input: 用户输入（可能是报告文本或分析需求）
            context: 知识库检索的参考信息
        """
        logger.info(f"[{self.name}] 开始分析报告")

        # 构建消息
        messages = self.build_messages(user_input, context)

        # 如果有文件路径，先解析
        file_path = kwargs.get("file_path")
        if file_path:
            parse_result = self.call_tool("parse_report_pdf", file_path=file_path)
            if parse_result.success:
                # 将解析结果加入上下文
                report_context = f"报告解析结果:\n{parse_result.result}"
                messages.insert(-1, {"role": "system", "content": report_context})

        # 调用LLM分析
        response = self.call_llm(messages)
        logger.info(f"[{self.name}] 分析完成")
        return response
