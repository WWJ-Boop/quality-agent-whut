"""趋势分析页面

检测数据的时间序列分析和可视化。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from agents.tools.data_analyzer import analyze_trend
from agents.tools.chart_generator import generate_trend_chart, generate_distribution_chart
import base64
from io import BytesIO


def render():
    """渲染趋势分析页面"""
    st.markdown("## 📈 检测数据趋势分析")
    st.markdown("分析检测数据的时间趋势，识别异常波动和质量风险")

    st.markdown("---")

    # 数据输入方式
    input_method = st.radio("数据输入方式", ["手动输入", "上传CSV", "使用演示数据"], horizontal=True)

    data = []

    if input_method == "手动输入":
        data = manual_input()
    elif input_method == "上传CSV":
        data = upload_csv()
    else:
        data = demo_data()

    if data:
        # 选择指标类型
        indicator_type = st.selectbox(
            "选择检测指标",
            ["混凝土抗压强度", "钢筋屈服强度", "坍落度", "回弹值"],
        )

        # 趋势分析
        st.markdown("---")
        st.markdown("### 分析结果")

        result = analyze_trend(data, indicator_type)

        # 统计指标
        col1, col2, col3, col4 = st.columns(4)
        stats = result["statistics"]

        with col1:
            st.metric("平均值", f"{stats['mean']:.2f}")
        with col2:
            st.metric("标准差", f"{stats['std']:.2f}")
        with col3:
            st.metric("变异系数", f"{stats['cv']:.1f}%")
        with col4:
            st.metric("趋势", result["trend"])

        # 图表
        unit_map = {
            "混凝土抗压强度": "MPa",
            "钢筋屈服强度": "MPa",
            "坍落度": "mm",
            "回弹值": "",
        }

        st.markdown("### 趋势图")
        try:
            chart_base64 = generate_trend_chart(
                data,
                title=f"{indicator_type}趋势图",
                indicator_name=indicator_type,
                unit=unit_map.get(indicator_type, ""),
            )
            st.image(BytesIO(base64.b64decode(chart_base64)), use_container_width=True)
        except Exception as e:
            st.error(f"趋势图生成失败: {e}")

        # 分布图
        st.markdown("### 分布图")
        try:
            values = [d["value"] for d in data]
            dist_base64 = generate_distribution_chart(
                values,
                title=f"{indicator_type}分布图",
                indicator_name=indicator_type,
                unit=unit_map.get(indicator_type, ""),
            )
            st.image(BytesIO(base64.b64decode(dist_base64)), use_container_width=True)
        except Exception as e:
            st.error(f"分布图生成失败: {e}")

        # 预警信息
        if result.get("warning"):
            st.warning(f"⚠️ {result['warning']}")

        # 数据表格
        st.markdown("### 数据明细")
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)


def manual_input():
    """手动输入数据"""
    st.markdown("### 输入检测数据")

    num_samples = st.number_input("样本数量", min_value=3, max_value=20, value=6)

    # 使用表单避免频繁刷新
    with st.form("data_input_form"):
        data = []
        cols = st.columns(2)

        with cols[0]:
            for i in range(num_samples // 2):
                date = st.date_input(
                    f"日期 {i+1}",
                    value=datetime.now() - timedelta(days=num_samples - i),
                    key=f"date_{i}",
                )
                value = st.number_input(
                    f"检测值 {i+1}",
                    min_value=0.0,
                    value=30.0,
                    key=f"value_{i}",
                )
                data.append({"date": date.strftime("%Y-%m-%d"), "value": value})

        with cols[1]:
            for i in range(num_samples // 2, num_samples):
                date = st.date_input(
                    f"日期 {i+1}",
                    value=datetime.now() - timedelta(days=num_samples - i),
                    key=f"date_{i}",
                )
                value = st.number_input(
                    f"检测值 {i+1}",
                    min_value=0.0,
                    value=30.0,
                    key=f"value_{i}",
                )
                data.append({"date": date.strftime("%Y-%m-%d"), "value": value})

        submitted = st.form_submit_button("开始分析")
        if submitted:
            return data

    return []


def upload_csv():
    """上传CSV数据"""
    uploaded_file = st.file_uploader("上传CSV文件", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head())

            # 选择列
            date_col = st.selectbox("选择日期列", df.columns)
            value_col = st.selectbox("选择数值列", df.columns)

            data = []
            for _, row in df.iterrows():
                data.append({
                    "date": str(row[date_col]),
                    "value": float(row[value_col]),
                })
            return data

        except Exception as e:
            st.error(f"文件解析失败: {e}")

    return []


def demo_data():
    """演示数据"""
    np.random.seed(42)
    dates = [(datetime.now() - timedelta(days=30 - i)).strftime("%Y-%m-%d") for i in range(30)]
    values = [30 + np.random.normal(0, 2) + 0.05 * i for i in range(30)]

    data = [{"date": d, "value": v} for d, v in zip(dates, values)]

    st.markdown("### 演示数据 (混凝土抗压强度)")
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    return data
