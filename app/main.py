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
    if "model_server" not in st.session_state:
        from model.inference.model_server import ModelServer
        server = ModelServer()
        server.initialize()
        st.session_state.model_server = server
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    if "coordinator" not in st.session_state:
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

    # 系统架构
    st.markdown("### 系统架构")
    st.markdown("""
    ```
    ┌─────────────────────────────────────────────────────────┐
    │                    前端展示层 (Streamlit)                  │
    │  [报告分析] [标准问答] [趋势分析] [报告生成]                   │
    ├─────────────────────────────────────────────────────────┤
    │                  Agent 编排层 (LangGraph)                  │
    │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
    │  │ 报告分析  │  │ 标准问答  │  │ 趋势分析  │               │
    │  │  Agent   │  │  Agent   │  │  Agent   │               │
    │  └──────────┘  └──────────┘  └──────────┘               │
    │                     协调Agent                             │
    ├─────────────────────────────────────────────────────────┤
    │  Qwen2.5-7B + LoRA微调 │  RAG知识库 (Milvus)             │
    └─────────────────────────────────────────────────────────┘
    ```
    """)

    # 技术栈
    st.markdown("### 技术栈")
    cols = st.columns(6)
    techs = ["Qwen2.5-7B", "LoRA微调", "LangGraph", "Milvus", "Streamlit", "RAG"]
    for col, tech in zip(cols, techs):
        with col:
            st.info(tech)


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
        st.success("✅ 系统就绪")

        if st.session_state.get("vector_store"):
            st.success("✅ 知识库已连接")
        else:
            st.warning("⚠️ 知识库未初始化")

        st.markdown("---")
        st.markdown("""
        **参赛信息**
        - 赛道：工程大模型 Agent 智能应用系统设计
        - 单位：武汉理工大学
        """)

    # 页面路由
    if page == "🏠 首页":
        render_home()
    elif page == "📊 报告分析":
        from app.pages.report_analysis import render
        render()
    elif page == "📚 标准问答":
        from app.pages.standard_qa import render
        render()
    elif page == "📈 趋势分析":
        from app.pages.trend_analysis import render
        render()
    elif page == "📝 报告生成":
        from app.pages.report_generate import render
        render()


if __name__ == "__main__":
    main()
