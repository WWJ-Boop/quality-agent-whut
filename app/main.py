"""智检通 - 主应用入口

工程质量检测分析智能体系统的Streamlit前端。
"""

import sys
from pathlib import Path

# 将项目根目录加入路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from loguru import logger

# 页面配置
st.set_page_config(
    page_title="智检通 - 工程质量检测分析智能体系统",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def init_session_state():
    """初始化会话状态"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # 演示模式不需要初始化模型
    st.session_state.model_server = None
    st.session_state.vector_store = None
    st.session_state.coordinator = None


def load_custom_css():
    """加载自定义样式"""
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)


def render_home():
    """渲染首页"""
    st.markdown('<div class="main-header">🏗️ 智检通</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">面向工程质量检测的多智能体分析系统</div>', unsafe_allow_html=True)

    st.markdown("---")

    # 功能介绍
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        ### 📊 报告分析
        自动解析检测报告PDF，提取关键指标，判定合格性
        """)

    with col2:
        st.markdown("""
        ### 📚 标准问答
        基于RAG的工程质量标准智能检索与问答
        """)

    with col3:
        st.markdown("""
        ### 📈 趋势分析
        检测数据时间序列分析，识别趋势和异常
        """)

    with col4:
        st.markdown("""
        ### 📝 报告生成
        根据检测数据自动生成规范报告
        """)

    st.markdown("---")

    # 系统架构图片
    st.image("assets/architecture.png", use_container_width=True, caption="系统架构图")

    # 技术栈
    st.markdown("### 技术栈")
    cols = st.columns(6)
    techs = ["Qwen2.5-7B", "LoRA微调", "LangGraph", "Milvus", "Streamlit", "RAG"]
    for col, tech in zip(cols, techs):
        with col:
            st.info(tech)


def render_report_analysis():
    """报告分析页面"""
    import re
    st.markdown("## 📊 检测报告分析")
    st.markdown("上传工程质量检测报告PDF文件，系统将自动解析并分析检测结果。")
    st.markdown("---")

    uploaded_file = st.file_uploader("上传检测报告", type=["pdf"], help="支持PDF格式的工程质量检测报告")

    if uploaded_file is not None:
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(uploaded_file)
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

            st.markdown("### 报告信息")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("文件名", uploaded_file.name)
            with col2:
                st.metric("页数", len(reader.pages))

            # 提取指标
            indicators = []
            pattern = r"(?:抗压强度|压力)[：:]\s*([\d.]+)\s*(?:MPa|mpa|兆帕)"
            for match in re.finditer(pattern, full_text):
                indicators.append({"type": "混凝土抗压强度", "value": float(match.group(1)), "unit": "MPa"})

            if indicators:
                st.markdown("### 检测指标分析")
                for ind in indicators:
                    with st.expander(f"{ind['type']}: {ind['value']}{ind.get('unit', '')}"):
                        if ind["value"] >= 30:
                            st.success(f"✅ 符合C30标准要求")
                        else:
                            st.error(f"❌ 低于C30最低要求30MPa")

                all_compliant = all(ind["value"] >= 30 for ind in indicators)
                if all_compliant:
                    st.success("✅ 该报告所有检测指标均符合标准要求")
                else:
                    st.warning("⚠️ 部分检测指标不符合标准要求")
            else:
                st.warning("未能从报告中提取到检测指标")

            with st.expander("查看报告原始文本"):
                st.text_area("", full_text[:5000], height=300)
        except Exception as e:
            st.error(f"解析失败: {e}")
    else:
        st.markdown("### 使用说明")
        st.markdown("1. 上传PDF格式的工程质量检测报告\n2. 系统自动解析报告内容\n3. 提取关键检测指标\n4. 对照标准进行合格性判定")

        st.markdown("### 演示数据")
        if st.button("使用演示数据", use_container_width=True):
            demo_indicators = [
                {"type": "混凝土抗压强度", "value": 32.5, "unit": "MPa"},
                {"type": "混凝土抗压强度", "value": 28.0, "unit": "MPa"},
                {"type": "混凝土抗压强度", "value": 35.2, "unit": "MPa"},
            ]
            for ind in demo_indicators:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(ind["type"])
                with col2:
                    st.write(f"{ind['value']}{ind['unit']}")
                with col3:
                    if ind["value"] >= 30:
                        st.success("合格")
                    else:
                        st.error("不合格")


def render_standard_qa():
    """标准问答页面"""
    def demo_answer(question):
        q = question.lower()
        if any(k in q for k in ["混凝土", "强度", "抗压", "c30"]):
            return "**混凝土强度评定标准 (GB/T 50107-2010)**\n\n- 统计法评定 (n≥10)：mfcu - λ₁×Sfcu ≥ fcu,k\n- 非统计法评定 (n<10)：mfcu ≥ 1.15×fcu,k"
        if any(k in q for k in ["钢筋", "hrb"]):
            return "**HRB400钢筋要求 (GB/T 1499.2-2018)**\n\n| 指标 | 标准要求 |\n|------|----------|\n| 屈服强度 | ≥400 MPa |\n| 抗拉强度 | ≥540 MPa |"
        if any(k in q for k in ["回弹", "碳化"]):
            return "**回弹法检测要点 (JGJ/T 23-2011)**\n\n- 每个构件≥10个测区\n- 每测区16个测点"
        if any(k in q for k in ["坍落"]):
            return "**混凝土坍落度检测 (GB/T 50080)**\n\n- 普通混凝土：70-180mm\n- 泵送混凝土：120-220mm"
        if any(k in q for k in ["桩基", "桩"]):
            return "**桩基检测方法 (JGJ 106-2014)**\n\n| 方法 | 检测内容 | 数量要求 |\n|------|---------|----------|\n| 静载试验 | 承载力 | 1%且≥3根 |\n| 低应变法 | 完整性 | 20%且≥10根 |"
        return "我是「智检通」工程质量检测助手，可以帮您查询标准规范、判定合格性等。请提出具体问题。"

    st.markdown("## 📚 工程质量标准问答")
    st.markdown("基于RAG知识库的工程质量标准智能检索与问答系统")
    st.markdown("---")

    if "qa_messages" not in st.session_state:
        st.session_state.qa_messages = []

    for msg in st.session_state.qa_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.markdown("### 常见问题")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("混凝土强度评定标准是什么？", use_container_width=True):
            q = "混凝土强度评定标准是什么？"
            st.session_state.qa_messages.append({"role": "user", "content": q})
            st.session_state.qa_messages.append({"role": "assistant", "content": demo_answer(q)})
            st.rerun()
        if st.button("钢筋取样频率规定？", use_container_width=True):
            q = "钢筋取样频率规定？"
            st.session_state.qa_messages.append({"role": "user", "content": q})
            st.session_state.qa_messages.append({"role": "assistant", "content": demo_answer(q)})
            st.rerun()
    with col2:
        if st.button("回弹法检测注意事项？", use_container_width=True):
            q = "回弹法检测注意事项？"
            st.session_state.qa_messages.append({"role": "user", "content": q})
            st.session_state.qa_messages.append({"role": "assistant", "content": demo_answer(q)})
            st.rerun()
        if st.button("坍落度检测方法？", use_container_width=True):
            q = "坍落度检测方法？"
            st.session_state.qa_messages.append({"role": "user", "content": q})
            st.session_state.qa_messages.append({"role": "assistant", "content": demo_answer(q)})
            st.rerun()

    user_input = st.chat_input("请输入关于工程质量标准的问题...")
    if user_input:
        st.session_state.qa_messages.append({"role": "user", "content": user_input})
        st.session_state.qa_messages.append({"role": "assistant", "content": demo_answer(user_input)})
        st.rerun()


def render_trend_analysis():
    """趋势分析页面"""
    import numpy as np
    import matplotlib.pyplot as plt
    from datetime import datetime, timedelta

    st.markdown("## 📈 检测数据趋势分析")
    st.markdown("分析检测数据的时间趋势，识别异常波动和质量风险")
    st.markdown("---")

    input_method = st.radio("数据输入方式", ["使用演示数据", "手动输入"], horizontal=True)
    data = []

    if input_method == "使用演示数据":
        np.random.seed(42)
        dates = [(datetime.now() - timedelta(days=30 - i)).strftime("%Y-%m-%d") for i in range(30)]
        values = [30 + np.random.normal(0, 2) + 0.05 * i for i in range(30)]
        data = [{"date": d, "value": v} for d, v in zip(dates, values)]
        st.dataframe(data, use_container_width=True)
    else:
        num_samples = st.number_input("样本数量", min_value=3, max_value=50, value=10)
        for i in range(num_samples):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input(f"日期 {i+1}", value=datetime.now() - timedelta(days=num_samples - i), key=f"date_{i}")
            with col2:
                value = st.number_input(f"检测值 {i+1}", min_value=0.0, value=30.0 + np.random.normal(0, 2), key=f"value_{i}")
            data.append({"date": date.strftime("%Y-%m-%d"), "value": value})

    if data:
        indicator_type = st.selectbox("选择检测指标", ["混凝土抗压强度", "钢筋屈服强度", "坍落度"])
        st.markdown("---")

        values = [d["value"] for d in data]
        arr = np.array(values)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("平均值", f"{np.mean(arr):.2f}")
        with col2:
            st.metric("标准差", f"{np.std(arr):.2f}")
        with col3:
            cv = np.std(arr) / np.mean(arr) * 100 if np.mean(arr) != 0 else 0
            st.metric("变异系数", f"{cv:.1f}%")
        with col4:
            slope = np.polyfit(np.arange(len(values)), arr, 1)[0]
            trend = "上升" if slope > 0.1 else "下降" if slope < -0.1 else "稳定"
            st.metric("趋势", trend)

        # 趋势图
        st.markdown("### 趋势图")
        fig, ax = plt.subplots(figsize=(10, 5))
        dates = [d["date"] for d in data]
        ax.plot(dates, values, 'b-o', linewidth=2, markersize=6)
        ax.axhline(y=np.mean(values), color='g', linestyle='--', alpha=0.7, label=f'均值: {np.mean(values):.1f}')
        ax.set_title(f"{indicator_type}趋势图")
        ax.set_xlabel("日期")
        ax.set_ylabel(indicator_type)
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)

        # 分布图
        st.markdown("### 分布图")
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        ax2.hist(values, bins=10, color='steelblue', edgecolor='white', alpha=0.8)
        ax2.axvline(x=np.mean(values), color='r', linestyle='--', label=f'均值: {np.mean(values):.1f}')
        ax2.set_title(f"{indicator_type}分布图")
        ax2.set_xlabel(indicator_type)
        ax2.set_ylabel("频次")
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        st.pyplot(fig2)

        if cv > 15:
            st.warning(f"⚠️ 变异系数({cv:.1f}%)较大，数据离散程度高")


def render_report_generate():
    """报告生成页面"""
    from datetime import datetime

    st.markdown("## 📝 检测报告生成")
    st.markdown("根据检测数据自动生成规范的质量检测报告")
    st.markdown("---")

    st.markdown("### 报告基本信息")
    col1, col2 = st.columns(2)
    with col1:
        project_name = st.text_input("工程名称", "XX住宅小区一期工程")
        client = st.text_input("委托单位", "XX建设集团有限公司")
        test_unit = st.text_input("检测单位", "XX工程质量检测中心")
    with col2:
        report_id = st.text_input("报告编号", f"JC-{datetime.now().strftime('%Y%m%d')}")
        test_date = st.date_input("检测日期", datetime.now())
        report_date = st.date_input("报告日期", datetime.now())

    st.markdown("### 检测项目")
    num_items = st.number_input("检测项目数量", min_value=1, max_value=10, value=3)
    test_items = []
    for i in range(num_items):
        col1, col2, col3 = st.columns(3)
        with col1:
            item_type = st.selectbox("检测项目", ["混凝土抗压强度", "钢筋屈服强度", "坍落度"], key=f"type_{i}")
        with col2:
            value = st.number_input("检测值", min_value=0.0, value=30.0, key=f"value_{i}")
        with col3:
            standard = st.text_input("标准/等级", "C30", key=f"standard_{i}")
        test_items.append({"name": item_type, "value": value, "standard": standard})

    st.markdown("---")
    if st.button("生成报告", type="primary", use_container_width=True):
        limits = {"混凝土抗压强度": 30, "钢筋屈服强度": 400}
        all_pass = all(item["value"] >= limits.get(item["name"], 0) for item in test_items)

        test_results = "| 序号 | 检测项目 | 检测值 | 标准要求 | 判定 |\n|------|---------|--------|---------|------|\n"
        for i, item in enumerate(test_items, 1):
            status = "合格" if item["value"] >= limits.get(item["name"], 0) else "不合格"
            test_results += f"| {i} | {item['name']} | {item['value']} | {item['standard']} | {status} |\n"

        conclusion = "经检测，所检项目均符合相关标准要求。" if all_pass else "经检测，部分项目不符合标准要求，建议复检。"

        report_content = f"""# 质量检测报告

| 项目 | 内容 |
|------|------|
| 报告编号 | {report_id} |
| 工程名称 | {project_name} |
| 委托单位 | {client} |
| 检测日期 | {test_date} |

## 检测项目及结果

{test_results}

## 检测结论

{conclusion}

---
检测单位: {test_unit}
报告日期: {report_date}
"""
        st.markdown(report_content)
        st.download_button("下载报告", report_content, file_name=f"检测报告_{report_id}.md", mime="text/markdown")

        total = len(test_items)
        passed = sum(1 for item in test_items if item["value"] >= limits.get(item["name"], 0))
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总项目数", total)
        with col2:
            st.metric("合格项目", passed)
        with col3:
            st.metric("不合格项目", total - passed)


def main():
    """主函数"""
    init_session_state()
    load_custom_css()

    # 侧边栏
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/construction.png", width=80)
        st.markdown("## 智检通")
        st.markdown("工程质量检测分析智能体系统")

        st.markdown("---")

        # 导航菜单
        page = st.radio(
            "功能导航",
            ["🏠 首页", "📊 报告分析", "📚 标准问答", "📈 趋势分析", "📝 报告生成"],
            index=0,
        )

        st.markdown("---")

        # 系统状态
        st.markdown("### 系统状态")
        st.success("✅ 系统就绪（演示模式）")
        st.info("💡 使用规则引擎，支持常见检测问题")

        st.markdown("---")
        st.markdown("""
        **参赛信息**
        - 赛道：工程大模型 Agent 智能应用系统设计
        - 单位：武汉理工大学
        - 参赛人员：吴武俊
        """)

    # 页面路由 - 使用演示模式
    if page == "🏠 首页":
        render_home()
    elif page == "📊 报告分析":
        render_report_analysis()
    elif page == "📚 标准问答":
        render_standard_qa()
    elif page == "📈 趋势分析":
        render_trend_analysis()
    elif page == "📝 报告生成":
        render_report_generate()


if __name__ == "__main__":
    main()
