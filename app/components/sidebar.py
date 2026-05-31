"""侧边栏组件"""

import streamlit as st


def render_sidebar():
    """渲染侧边栏"""
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

        st.markdown("---")
        st.markdown("""
        **参赛信息**
        - 赛道：工程大模型 Agent 智能应用系统设计
        - 单位：武汉理工大学
        """)

        return page
