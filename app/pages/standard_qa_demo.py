"""标准问答页面 - 演示模式"""

import streamlit as st


def demo_answer(question):
    """演示模式问答"""
    q = question.lower()
    if any(k in q for k in ["混凝土", "强度", "抗压", "c30"]):
        return "**混凝土强度评定标准 (GB/T 50107-2010)**\n\n- 统计法评定 (n≥10)：mfcu - λ₁×Sfcu ≥ fcu,k\n- 非统计法评定 (n<10)：mfcu ≥ 1.15×fcu,k"
    if any(k in q for k in ["钢筋", "hrb"]):
        return "**HRB400钢筋要求 (GB/T 1499.2-2018)**\n\n| 指标 | 标准要求 |\n|------|----------|\n| 屈服强度 | ≥400 MPa |\n| 抗拉强度 | ≥540 MPa |"
    if any(k in q for k in ["回弹", "碳化"]):
        return "**回弹法检测要点 (JGJ/T 23-2011)**\n\n- 每个构件≥10个测区\n- 每测区16个测点\n- 距构件边缘≥0.2m"
    if any(k in q for k in ["坍落"]):
        return "**混凝土坍落度检测 (GB/T 50080)**\n\n- 普通混凝土：70-180mm\n- 泵送混凝土：120-220mm"
    if any(k in q for k in ["桩基", "桩"]):
        return "**桩基检测方法 (JGJ 106-2014)**\n\n| 方法 | 检测内容 | 数量要求 |\n|------|---------|----------|\n| 静载试验 | 承载力 | 1%且≥3根 |\n| 低应变法 | 完整性 | 20%且≥10根 |"
    return "我是「智检通」工程质量检测助手，可以帮您查询标准规范、判定合格性等。请提出具体问题。"


def render():
    """渲染标准问答页面"""
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
