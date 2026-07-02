"""趋势分析页面 - 演示模式"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import io
import base64


def render():
    """渲染趋势分析页面"""
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
            trend = "上升" if np.polyfit(np.arange(len(values)), arr, 1)[0] > 0.1 else "下降" if np.polyfit(np.arange(len(values)), arr, 1)[0] < -0.1 else "稳定"
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
