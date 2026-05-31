"""报告分析页面

上传检测报告PDF，自动解析并分析。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import tempfile
import os
from agents.tools.pdf_parser import parse_report_pdf, extract_indicators
from agents.tools.data_analyzer import check_compliance


def render():
    """渲染报告分析页面"""
    st.markdown("## 📊 检测报告分析")
    st.markdown("上传工程质量检测报告PDF文件，系统将自动解析并分析检测结果。")

    st.markdown("---")

    # 文件上传
    uploaded_file = st.file_uploader(
        "上传检测报告",
        type=["pdf"],
        help="支持PDF格式的工程质量检测报告",
    )

    if uploaded_file is not None:
        # 保存上传的文件到临时目录
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            with st.spinner("正在解析报告..."):
                result = parse_report_pdf(tmp_path)

            if "error" in result:
                st.error(f"解析失败: {result['error']}")
                return

            # 显示报告基本信息
            st.markdown("### 报告信息")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("文件名", result.get("file_name", ""))
            with col2:
                st.metric("页数", result.get("total_pages", 0))
            with col3:
                st.metric("提取指标数", len(result.get("indicators", [])))

            # 显示报告详细信息
            report_info = result.get("report_info", {})
            if report_info:
                st.markdown("### 工程信息")
                info_cols = st.columns(2)
                with info_cols[0]:
                    if "project_name" in report_info:
                        st.info(f"**工程名称**: {report_info['project_name']}")
                    if "client" in report_info:
                        st.info(f"**委托单位**: {report_info['client']}")
                with info_cols[1]:
                    if "date" in report_info:
                        st.info(f"**检测日期**: {report_info['date']}")
                    if "design_strength" in report_info:
                        st.info(f"**设计强度**: {report_info['design_strength']}")

            # 显示提取的指标
            indicators = result.get("indicators", [])
            if indicators:
                st.markdown("### 检测指标分析")

                for i, ind in enumerate(indicators):
                    with st.expander(f"{ind['type']}: {ind['value']}{ind.get('unit', '')}"):
                        # 合格性判定
                        compliance = check_compliance(
                            indicator_type=ind["type"],
                            value=ind["value"],
                            standard=report_info.get("design_strength", ""),
                        )

                        if compliance["is_compliant"]:
                            st.success(f"✅ {compliance['details']}")
                        else:
                            st.error(f"❌ {compliance['details']}")

                        st.json(ind)

                # 综合结论
                st.markdown("### 综合分析结论")
                all_compliant = all(
                    check_compliance(
                        ind["type"],
                        ind["value"],
                        report_info.get("design_strength", ""),
                    )["is_compliant"]
                    for ind in indicators
                )

                if all_compliant:
                    st.success("✅ 该报告所有检测指标均符合标准要求")
                else:
                    st.warning("⚠️ 部分检测指标不符合标准要求，请查看详情")

            else:
                st.warning("未能从报告中提取到检测指标，请检查报告格式")

            # 显示原始文本
            with st.expander("查看报告原始文本"):
                st.text_area("", result.get("raw_text", "")[:5000], height=300)

        finally:
            # 清理临时文件
            os.unlink(tmp_path)

    else:
        # 显示示例
        st.markdown("### 使用说明")
        st.markdown("""
        1. 上传PDF格式的工程质量检测报告
        2. 系统自动解析报告内容
        3. 提取关键检测指标（混凝土强度、钢筋性能等）
        4. 对照标准进行合格性判定
        5. 生成分析结论
        """)

        st.markdown("### 支持的报告类型")
        st.markdown("""
        - 混凝土抗压强度检测报告
        - 钢筋力学性能检测报告
        - 混凝土坍落度检测报告
        - 回弹法检测报告
        - 桩基检测报告
        """)

        # 演示数据
        st.markdown("### 演示数据")
        if st.button("使用演示数据"):
            demo_indicators = [
                {"type": "混凝土抗压强度", "value": 32.5, "unit": "MPa"},
                {"type": "混凝土抗压强度", "value": 28.0, "unit": "MPa"},
                {"type": "混凝土抗压强度", "value": 35.2, "unit": "MPa"},
            ]

            st.markdown("#### 检测指标")
            for ind in demo_indicators:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(ind["type"])
                with col2:
                    st.write(f"{ind['value']}{ind['unit']}")
                with col3:
                    result = check_compliance(ind["type"], ind["value"], "C30")
                    if result["is_compliant"]:
                        st.success("合格")
                    else:
                        st.error("不合格")
