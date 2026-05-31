"""模型推理服务

提供统一的LLM调用接口，支持本地模型、商用API和演示模式。
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Callable
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class ModelServer:
    """模型推理服务

    支持三种模式:
    1. 本地模型: 加载微调后的Qwen模型 (需要GPU)
    2. 商用API: 调用OpenAI兼容接口
    3. 演示模式: 基于规则的智能回复 (无需GPU和API)
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model_name: str = "gpt-3.5-turbo",
        device: str = "auto",
    ):
        self.model_path = model_path
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_base = api_base or os.getenv("OPENAI_BASE_URL")
        self.model_name = model_name
        self.device = device

        self._model = None
        self._tokenizer = None
        self._use_api = False
        self._use_demo = False

    def initialize(self):
        """初始化模型"""
        if self.model_path and Path(self.model_path).exists():
            self._load_local_model()
        elif self.api_key:
            self._use_api = True
            logger.info(f"使用API模式: {self.model_name}")
        else:
            self._use_demo = True
            logger.info("使用演示模式 (无需API密钥)")

    def _load_local_model(self):
        """加载本地模型"""
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        logger.info(f"加载本地模型: {self.model_path}")
        self._tokenizer = AutoTokenizer.from_pretrained(
            self.model_path, trust_remote_code=True
        )
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            torch_dtype=torch.bfloat16,
            device_map=self.device,
            trust_remote_code=True,
        )
        logger.info("本地模型加载完成")

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """对话接口"""
        if self._use_demo:
            return self._chat_demo(messages, **kwargs)
        elif self._use_api:
            return self._chat_api(messages, **kwargs)
        else:
            return self._chat_local(messages, **kwargs)

    def _chat_demo(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """演示模式: 基于规则的智能回复"""
        user_msg = ""
        system_msg = ""
        for msg in messages:
            if msg["role"] == "user":
                user_msg = msg["content"]
            elif msg["role"] == "system":
                system_msg = msg["content"]

        # 提取上下文信息
        context = ""
        if "参考" in system_msg or "检索" in system_msg:
            context = system_msg

        return self._generate_demo_response(user_msg, context)

    def _generate_demo_response(self, question: str, context: str = "") -> str:
        """生成演示回复"""
        q = question.lower()

        # 混凝土强度相关
        if any(k in q for k in ["混凝土", "强度", "抗压", "c30", "c35", "c40", "试块"]):
            return self._demo_concrete_strength(question, context)

        # 钢筋相关
        if any(k in q for k in ["钢筋", "hrb", "屈服", "抗拉", "hpb"]):
            return self._demo_steel(question, context)

        # 回弹法
        if any(k in q for k in ["回弹", "碳化"]):
            return self._demo_rebound(question, context)

        # 坍落度
        if any(k in q for k in ["坍落", "流动性", "工作性"]):
            return self._demo_slump(question, context)

        # 桩基
        if any(k in q for k in ["桩基", "桩", "静载", "高应变", "低应变"]):
            return self._demo_pile(question, context)

        # 取样
        if any(k in q for k in ["取样", "频率", "数量", "批次"]):
            return self._demo_sampling(question, context)

        # 报告生成
        if any(k in q for k in ["报告", "生成", "撰写"]):
            return self._demo_report(question, context)

        # 标准规范
        if any(k in q for k in ["标准", "规范", "gb", "jgj", "条文"]):
            return self._demo_standard(question, context)

        # 通用回复
        if context:
            return f"根据知识库检索到的信息：\n\n{context}\n\n以上是与您问题相关的标准条文内容。如需更详细的信息，请提供更具体的问题。"

        return ("我是「智检通」工程质量检测分析助手，可以帮您：\n\n"
                "1. **分析检测报告** - 上传PDF自动解析\n"
                "2. **查询标准规范** - 如「混凝土强度评定标准是什么」\n"
                "3. **分析数据趋势** - 检测数据的统计分析\n"
                "4. **生成检测报告** - 自动生成规范报告\n\n"
                "请告诉我您需要什么帮助？")

    def _demo_concrete_strength(self, q: str, ctx: str) -> str:
        """混凝土强度相关回复"""
        # 尝试提取数值
        nums = re.findall(r'[\d.]+', q)

        if "合格" in q or "是否" in q:
            if nums:
                val = float(nums[0])
                grade = "C30"
                for g in ["C20", "C25", "C30", "C35", "C40", "C45", "C50"]:
                    if g.lower() in q.lower():
                        grade = g
                        break
                std_val = int(grade[1:])
                if val >= std_val:
                    return (f"检测值 {val}MPa ≥ 设计强度 {grade}({std_val}MPa)\n\n"
                            f"**判定结论：合格** ✅\n\n"
                            f"依据 GB/T 50107-2010《混凝土强度检验评定标准》，"
                            f"该批次混凝土强度满足 {grade} 设计要求。")
                else:
                    return (f"检测值 {val}MPa < 设计强度 {grade}({std_val}MPa)\n\n"
                            f"**判定结论：不合格** ❌\n\n"
                            f"依据 GB/T 50107-2010，该批次混凝土强度不满足 {grade} 要求。\n\n"
                            f"**建议措施：**\n"
                            f"1. 进行回弹法或钻芯法复检\n"
                            f"2. 查找强度不足原因（配合比、养护条件等）\n"
                            f"3. 必要时进行结构安全性评估")

        if "评定" in q or "标准" in q:
            return ("**混凝土强度评定标准 (GB/T 50107-2010)**\n\n"
                    "**统计法评定 (n≥10)：**\n"
                    "1. mfcu - λ₁×Sfcu ≥ fcu,k\n"
                    "2. fcu,min ≥ λ₂×fcu,k\n\n"
                    "其中：\n"
                    "- mfcu: 强度平均值\n"
                    "- Sfcu: 强度标准差\n"
                    "- fcu,k: 设计强度标准值\n"
                    "- λ₁=1.70, λ₂=0.90 (n=10-14)\n\n"
                    "**非统计法评定 (n<10)：**\n"
                    "1. mfcu ≥ 1.15×fcu,k\n"
                    "2. fcu,min ≥ 0.95×fcu,k")

        return ("**混凝土强度检测要点：**\n\n"
                "- 标准养护条件：温度20±2℃，湿度≥95%\n"
                "- 标准龄期：28天\n"
                "- 试件尺寸：150mm立方体\n"
                "- 依据标准：GB/T 50081, GB/T 50107\n\n"
                "如需具体判定，请提供检测值和设计强度等级。")

    def _demo_steel(self, q: str, ctx: str) -> str:
        """钢筋相关回复"""
        if "hrb400" in q.lower():
            return ("**HRB400钢筋力学性能要求 (GB/T 1499.2-2018)**\n\n"
                    "| 指标 | 标准要求 |\n"
                    "|------|----------|\n"
                    "| 屈服强度 ReL | ≥400 MPa |\n"
                    "| 抗拉强度 Rm | ≥540 MPa |\n"
                    "| 强屈比 Rm/ReL | ≥1.25 |\n"
                    "| 超屈比 ReL实测/400 | ≤1.30 |\n"
                    "| 最大力总延伸率 Agt | ≥7.5% |")

        if "取样" in q or "频率" in q:
            return self._demo_sampling(q, ctx)

        return ("**钢筋检测要点：**\n\n"
                "- 取样标准：GB/T 1499.2-2018\n"
                "- 每批≤60t，取拉伸2根+弯曲2根\n"
                "- 检测项目：屈服强度、抗拉强度、伸长率、弯曲\n"
                "- 常用牌号：HRB400, HRB500")

    def _demo_rebound(self, q: str, ctx: str) -> str:
        """回弹法相关回复"""
        return ("**回弹法检测要点 (JGJ/T 23-2011)**\n\n"
                "**测区布置：**\n"
                "- 每个构件≥10个测区\n"
                "- 测区间距≤2m\n"
                "- 距构件边缘≥0.2m\n\n"
                "**测点要求：**\n"
                "- 每测区16个测点\n"
                "- 测点间距≥20mm\n"
                "- 避开气孔和外露石子\n\n"
                "**碳化深度修正：**\n"
                "- 用酚酞试剂测量碳化深度\n"
                "- 碳化使表面硬度增加，回弹值偏高\n"
                "- 必须结合碳化深度查表换算强度\n\n"
                "**注意事项：**\n"
                "- 检测面应清洁、干燥\n"
                "- 回弹仪使用前需率定\n"
                "- 去除3个最大值和3个最小值后取平均")

    def _demo_slump(self, q: str, ctx: str) -> str:
        """坍落度相关回复"""
        return ("**混凝土坍落度检测 (GB/T 50080)**\n\n"
                "**检测步骤：**\n"
                "1. 润湿坍落度筒及底板\n"
                "2. 将混凝土分三层装入筒内\n"
                "3. 每层用捣棒插捣25次\n"
                "4. 刮平顶面\n"
                "5. 5-10秒内垂直提起筒\n"
                "6. 测量筒顶与坍落后混凝土最高点的高度差\n\n"
                "**常用范围：**\n"
                "- 普通混凝土：70-180mm\n"
                "- 泵送混凝土：120-220mm\n"
                "- 大流动性混凝土：≥160mm\n\n"
                "**注意事项：**\n"
                "- 出机后尽快完成检测\n"
                "- 同一试样测两次取平均值")

    def _demo_pile(self, q: str, ctx: str) -> str:
        """桩基相关回复"""
        return ("**桩基检测方法 (JGJ 106-2014)**\n\n"
                "| 方法 | 检测内容 | 数量要求 |\n"
                "|------|---------|----------|\n"
                "| 静载试验 | 承载力 | 1%且≥3根 |\n"
                "| 高应变法 | 承载力+完整性 | 5%且≥5根 |\n"
                "| 低应变法 | 完整性 | 20%且≥10根 |\n"
                "| 声波透射法 | 完整性 | 10%且≥10根 |\n"
                "| 钻芯法 | 强度+完整性 | 按需 |")

    def _demo_sampling(self, q: str, ctx: str) -> str:
        """取样频率相关回复"""
        return ("**钢筋取样规定 (GB/T 1499.2-2018)**\n\n"
                "**组批规则：**\n"
                "同一牌号、炉罐号、规格、交货状态为一批，每批≤60t\n\n"
                "**取样数量：**\n"
                "- 拉伸试验：每批2根\n"
                "- 弯曲试验：每批2根\n"
                "- 重量偏差：每批5根（长度≥500mm）\n\n"
                "**取样位置：**\n"
                "- 从不同根钢筋截取\n"
                "- 距钢筋端部≥500mm\n"
                "- 避免在弯折处取样\n\n"
                "**复检规则：**\n"
                "初检不合格时，取双倍试样复检。复检仍不合格，判定该批不合格。")

    def _demo_report(self, q: str, ctx: str) -> str:
        """报告生成相关回复"""
        return ("**检测报告应包含以下内容：**\n\n"
                "1. **基本信息** - 报告编号、工程名称、委托单位、检测日期\n"
                "2. **工程概况** - 结构类型、设计强度、浇筑部位\n"
                "3. **检测依据** - 引用的国家标准和行业规范\n"
                "4. **检测数据** - 各项检测指标及结果\n"
                "5. **合格判定** - 对照标准的合格/不合格结论\n"
                "6. **检测结论** - 综合评定意见\n"
                "7. **签章** - 检测人员、审核人员签名及公章")

    def _demo_standard(self, q: str, ctx: str) -> str:
        """标准规范相关回复"""
        if ctx:
            return f"根据知识库检索：\n\n{ctx}\n\n以上是相关标准条文内容。"
        return ("**常用工程质量标准：**\n\n"
                "- GB/T 50107 混凝土强度检验评定标准\n"
                "- GB 50204 混凝土结构工程施工质量验收规范\n"
                "- GB/T 50081 混凝土力学性能试验方法标准\n"
                "- GB/T 228.1 金属材料拉伸试验\n"
                "- GB/T 1499.2 钢筋混凝土用钢\n"
                "- JGJ/T 23 回弹法检测混凝土抗压强度技术规程\n\n"
                "请提出具体问题，我会检索相关条文为您解答。")

    def _chat_local(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """本地模型推理"""
        import torch

        if self._model is None:
            self.initialize()

        text = self._tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self._tokenizer([text], return_tensors="pt").to(self._model.device)

        temperature = kwargs.get("temperature", 0.1)
        max_tokens = kwargs.get("max_tokens", 2048)

        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                top_p=kwargs.get("top_p", 0.9),
            )

        response = self._tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[-1]:],
            skip_special_tokens=True,
        )
        return response

    def _chat_api(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """API调用"""
        from openai import OpenAI

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base,
        )

        response = client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=kwargs.get("temperature", 0.1),
            max_tokens=kwargs.get("max_tokens", 2048),
        )

        return response.choices[0].message.content

    def get_llm_caller(self) -> Callable:
        """获取LLM调用函数，供Agent使用"""
        def caller(messages: List[Dict[str, str]]) -> str:
            return self.chat(messages)
        return caller


_server: Optional[ModelServer] = None


def get_model_server() -> ModelServer:
    """获取全局模型服务实例"""
    global _server
    if _server is None:
        _server = ModelServer()
    return _server


def create_model_server(
    model_path: Optional[str] = None,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    **kwargs,
) -> ModelServer:
    """创建模型服务实例"""
    global _server
    _server = ModelServer(
        model_path=model_path,
        api_key=api_key,
        api_base=api_base,
        **kwargs,
    )
    return _server
