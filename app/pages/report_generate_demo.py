"""报告生成页面 - 演示模式"""

import streamlit as st
from datetime import datetime


def render():
    """渲染报告生成页面"""
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
        # 简单判定
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

        # 统计
        total = len(test_items)
        passed = sum(1 for item in test_items if item["value"] >= limits.get(item["name"], 0))
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总项目数", total)
        with col2:
            st.metric("合格项目", passed)
        with col3:
            st.metric("不合格项目", total - passed)
