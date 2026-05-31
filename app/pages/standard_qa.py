"""标准问答页面

基于RAG知识库的工程质量标准智能问答。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st


def render():
    """渲染标准问答页面"""
    st.markdown("## 📚 工程质量标准问答")
    st.markdown("基于RAG知识库的工程质量标准智能检索与问答系统")

    st.markdown("---")

    # 初始化会话消息
    if "qa_messages" not in st.session_state:
        st.session_state.qa_messages = []

    # 显示历史消息
    for msg in st.session_state.qa_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 预设问题
    st.markdown("### 常见问题")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("混凝土强度评定标准是什么？"):
            ask_question("混凝土强度评定标准是什么？依据哪个规范？")

        if st.button("钢筋取样频率规定？"):
            ask_question("钢筋力学性能检测的取样频率和数量是如何规定的？")

    with col2:
        if st.button("回弹法检测注意事项？"):
            ask_question("回弹法检测混凝土强度时需要注意哪些事项？")

        if st.button("坍落度检测方法？"):
            ask_question("混凝土坍落度的检测方法和步骤是什么？")

    # 用户输入
    user_input = st.chat_input("请输入关于工程质量标准的问题...")

    if user_input:
        ask_question(user_input)


def ask_question(question: str):
    """提问并获取回答"""
    st.session_state.qa_messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("正在检索标准知识库..."):
            response = get_answer(question)
            st.markdown(response)

    st.session_state.qa_messages.append({"role": "assistant", "content": response})


def get_answer(question: str) -> str:
    """获取标准问答的回答"""
    # 尝试RAG检索
    context = ""
    try:
        from knowledge import EmbeddingModel, VectorStore

        if "vector_store" not in st.session_state or st.session_state.vector_store is None:
            embedding_model = EmbeddingModel()
            vector_store = VectorStore(embedding_model=embedding_model)
            vector_store.connect()
            st.session_state.vector_store = vector_store

        results = st.session_state.vector_store.search(question, top_k=3)
        if results:
            context = "\n\n".join([f"【{r.metadata.get('filename', '')}】\n{r.content}" for r in results])
    except Exception:
        pass

    # 使用模型服务生成回答
    server = st.session_state.get("model_server")
    if server:
        messages = [
            {"role": "system", "content": f"你是工程质量检测标准问答专家。以下是检索到的相关标准条文:\n{context}" if context else "你是工程质量检测标准问答专家。"},
            {"role": "user", "content": question},
        ]
        return server.chat(messages)

    # 兜底
    if context:
        return f"根据知识库检索：\n\n{context}"
    return "系统初始化中，请稍后再试。"
