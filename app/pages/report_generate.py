"""报告生成页面

根据检测数据自动生成规范的检测报告。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from datetime import datetime
from agents.tools.report_writer import generate_report
from agents.tools.data_analyzer import check_compliance


def render():
    """渲染报告生成页面"""
    st.markdown("## 📝 检测报告生成")
    st.markdown("根据检测数据自动生成规范的质量检测报告")

    st.markdown("---")

    # 报告基本信息
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

    # 检测项目
    st.markdown("### 检测项目")

    num_items = st.number_input("检测项目数量", min_value=1, max_value=20, value=3)

    test_items = []
    for i in range(num_items):
        st.markdown(f"#### 项目 {i+1}")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            item_type = st.selectbox(
                "检测项目",
                ["混凝土抗压强度", "钢筋屈服强度", "钢筋抗拉强度", "坍落度", "回弹值"],
                key=f"type_{i}",
            )

        with col2:
            value = st.number_input("检测值", min_value=0.0, value=30.0, key=f"value_{i}")

        with col3:
            unit_map = {
                "混凝土抗压强度": "MPa",
                "钢筋屈服强度": "MPa",
                "钢筋抗拉强度": "MPa",
                "坍落度": "mm",
                "回弹值": "",
            }
            st.text_input("单位", unit_map.get(item_type, ""), key=f"unit_{i}", disabled=True)

        with col4:
            standard = st.text_input("标准/等级", "C30", key=f"standard_{i}")

        # 合格性判定
        result = check_compliance(item_type, value, standard)
        is_compliant = result["is_compliant"]

        test_items.append({
            "name": item_type,
            "value": value,
            "unit": unit_map.get(item_type, ""),
            "standard": standard,
            "is_compliant": is_compliant,
        })

    # 检测依据
    st.markdown("### 检测依据")
    standards = st.text_area(
        "检测依据标准",
        "1. GB/T 50107-2010 混凝土强度检验评定标准\n"
        "2. GB 50204-2015 混凝土结构工程施工质量验收规范\n"
        "3. GB/T 1499.2-2018 钢筋混凝土用钢 第2部分：热轧带肋钢筋",
        height=150,
    )

    # 工程概况
    project_desc = st.text_area(
        "工程概况",
        "根据委托方要求，对本工程相关材料/构件进行质量检测。",
        height=100,
    )

    # 输出格式
    output_format = st.radio("输出格式", ["markdown", "text"], horizontal=True)

    # 生成报告
    st.markdown("---")

    if st.button("生成报告", type="primary", use_container_width=True):
        report_data = {
            "report_id": report_id,
            "project_name": project_name,
            "client": client,
            "test_unit": test_unit,
            "date": test_date.strftime("%Y-%m-%d"),
            "report_date": report_date.strftime("%Y-%m-%d"),
            "test_items": test_items,
            "standards": standards,
            "project_desc": project_desc,
        }

        with st.spinner("正在生成报告..."):
            report_content = generate_report(report_data, output_format)

        st.markdown("### 生成的报告")

        if output_format == "markdown":
            st.markdown(report_content)
        else:
            st.text_area("", report_content, height=600)

        # 下载按钮
        st.download_button(
            label="下载报告",
            data=report_content,
            file_name=f"检测报告_{report_id}.md" if output_format == "markdown" else f"检测报告_{report_id}.txt",
            mime="text/markdown" if output_format == "markdown" else "text/plain",
        )

        # 合格性统计
        st.markdown("### 合格性统计")
        total = len(test_items)
        passed = sum(1 for item in test_items if item["is_compliant"])
        failed = total - passed

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总项目数", total)
        with col2:
            st.metric("合格项目", passed)
        with col3:
            st.metric("不合格项目", failed)
