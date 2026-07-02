"""报告分析页面 - 演示模式"""

import streamlit as st
import re


def check_compliance(indicator_type, value, standard="C30"):
    """检查指标合格性"""
    limits = {
        "混凝土抗压强度": {"C20": 20, "C25": 25, "C30": 30, "C35": 35, "C40": 40},
        "钢筋屈服强度": {"HRB400": 400},
    }
    if indicator_type in limits and standard in limits[indicator_type]:
        min_val = limits[indicator_type][standard]
        if value >= min_val:
            return {"is_compliant": True, "details": f"符合{standard}标准要求"}
        else:
            return {"is_compliant": False, "details": f"低于{standard}最低要求{min_val}"}
    return {"is_compliant": True, "details": "无法判定"}


def render():
    """渲染报告分析页面"""
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
                        compliance = check_compliance(ind["type"], ind["value"], "C30")
                        if compliance["is_compliant"]:
                            st.success(f"✅ {compliance['details']}")
                        else:
                            st.error(f"❌ {compliance['details']}")

                all_compliant = all(check_compliance(ind["type"], ind["value"], "C30")["is_compliant"] for ind in indicators)
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
                    result = check_compliance(ind["type"], ind["value"], "C30")
                    if result["is_compliant"]:
                        st.success("合格")
                    else:
                        st.error("不合格")
