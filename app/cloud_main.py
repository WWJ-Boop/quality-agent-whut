"""智检通 - 云端部署版主入口（Linear设计风格）

面向Streamlit Cloud的轻量版本，使用演示模式运行。
设计风格：Linear-inspired 极简深色主题

版本: 1.2.0 - 架构图显示优化
"""

import sys
from pathlib import Path

# 将项目根目录加入路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import re
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import io
import base64

# 页面配置
st.set_page_config(
    page_title="智检通 - 工程质量检测智能分析",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ============================================================
# Linear-inspired CSS Design System
# ============================================================

st.markdown("""
<style>
    /* Import Inter font - closest to Linear's custom sans */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Linear Color System */
    :root {
        --canvas: #010102;
        --surface-1: #0f1011;
        --surface-2: #141516;
        --surface-3: #18191a;
        --surface-4: #191a1b;
        --hairline: #23252a;
        --hairline-strong: #34343a;
        --ink: #f7f8f8;
        --ink-muted: #d0d6e0;
        --ink-subtle: #8a8f98;
        --ink-tertiary: #62666d;
        --primary: #5e6ad2;
        --primary-hover: #828fff;
        --primary-focus: #5e69d1;
        --success: #27a644;
    }

    /* Global Styles */
    .stApp {
        background-color: var(--canvas);
        font-family: 'Inter', -apple-system, system-ui, sans-serif;
    }

    .stApp > header {
        background-color: transparent;
    }

    /* Main Content Area */
    .main .block-container {
        max-width: 1280px;
        padding: 2rem 3rem;
    }

    /* Text Colors */
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        color: var(--ink);
    }

    /* Display Typography - Aggressive negative tracking like Linear */
    .display-xl {
        font-size: 4rem;
        font-weight: 600;
        line-height: 1.05;
        letter-spacing: -3px;
        color: var(--ink);
    }

    .display-lg {
        font-size: 3rem;
        font-weight: 600;
        line-height: 1.10;
        letter-spacing: -1.8px;
        color: var(--ink);
    }

    .display-md {
        font-size: 2rem;
        font-weight: 600;
        line-height: 1.15;
        letter-spacing: -1px;
        color: var(--ink);
    }

    .headline {
        font-size: 1.5rem;
        font-weight: 600;
        line-height: 1.20;
        letter-spacing: -0.6px;
        color: var(--ink);
    }

    .card-title {
        font-size: 1.25rem;
        font-weight: 500;
        line-height: 1.25;
        letter-spacing: -0.4px;
        color: var(--ink);
    }

    .body-lg {
        font-size: 1.125rem;
        font-weight: 400;
        line-height: 1.50;
        color: var(--ink-muted);
    }

    .body {
        font-size: 1rem;
        font-weight: 400;
        line-height: 1.50;
        color: var(--ink-muted);
    }

    .body-sm {
        font-size: 0.875rem;
        font-weight: 400;
        line-height: 1.50;
        color: var(--ink-subtle);
    }

    .caption {
        font-size: 0.75rem;
        font-weight: 400;
        line-height: 1.40;
        color: var(--ink-tertiary);
    }

    .eyebrow {
        font-size: 0.8125rem;
        font-weight: 500;
        line-height: 1.30;
        letter-spacing: 0.4px;
        text-transform: uppercase;
        color: var(--ink-subtle);
    }

    /* Hero Section */
    .hero-container {
        padding: 4rem 0;
        text-align: center;
    }

    .hero-badge {
        display: inline-block;
        background: var(--surface-2);
        color: var(--primary);
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8125rem;
        font-weight: 500;
        letter-spacing: 0.4px;
        margin-bottom: 1.5rem;
        border: 1px solid var(--hairline);
    }

    /* Surface Cards - Linear style */
    .surface-card {
        background: var(--surface-1);
        border: 1px solid var(--hairline);
        border-radius: 12px;
        padding: 24px;
        transition: border-color 0.2s ease;
    }

    .surface-card:hover {
        border-color: var(--hairline-strong);
    }

    .surface-card-featured {
        background: var(--surface-2);
        border: 1px solid var(--hairline-strong);
        border-radius: 12px;
        padding: 24px;
    }

    /* Feature Cards */
    .feature-card {
        background: var(--surface-1);
        border: 1px solid var(--hairline);
        border-radius: 12px;
        padding: 24px;
        height: 100%;
        transition: all 0.2s ease;
    }

    .feature-card:hover {
        border-color: var(--primary);
        transform: translateY(-2px);
    }

    .feature-card .icon {
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }

    .feature-card h3 {
        font-size: 1.25rem;
        font-weight: 500;
        letter-spacing: -0.4px;
        margin-bottom: 0.5rem;
        color: var(--ink);
    }

    .feature-card p {
        font-size: 0.875rem;
        color: var(--ink-subtle);
        line-height: 1.50;
        margin: 0;
    }

    /* Architecture Layers */
    .arch-layer {
        background: var(--surface-1);
        border: 1px solid var(--hairline);
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .arch-layer-icon {
        width: 40px;
        height: 40px;
        background: var(--surface-2);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        flex-shrink: 0;
    }

    .arch-layer-content h4 {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--ink);
        margin: 0 0 2px 0;
    }

    .arch-layer-content p {
        font-size: 0.75rem;
        color: var(--ink-subtle);
        margin: 0;
    }

    /* Tech Tags */
    .tech-tag {
        display: inline-block;
        background: var(--surface-2);
        color: var(--ink-muted);
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 500;
        margin: 4px;
        border: 1px solid var(--hairline);
    }

    /* Metric Cards */
    .metric-card {
        background: var(--surface-1);
        border: 1px solid var(--hairline);
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }

    .metric-card .value {
        font-size: 2rem;
        font-weight: 600;
        color: var(--ink);
        letter-spacing: -1px;
        margin: 0;
    }

    .metric-card .label {
        font-size: 0.75rem;
        color: var(--ink-subtle);
        margin-top: 4px;
    }

    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
    }

    .status-badge-success {
        background: rgba(39, 166, 68, 0.15);
        color: var(--success);
    }

    .status-badge-error {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
    }

    /* Sidebar - Linear style */
    [data-testid="stSidebar"] {
        background: var(--surface-1);
        border-right: 1px solid var(--hairline);
    }

    [data-testid="stSidebar"] .block-container {
        padding: 1.5rem;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        color: var(--ink-muted) !important;
        font-size: 0.875rem;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] {
        color: var(--ink) !important;
        background: var(--surface-2);
        border-radius: 6px;
    }

    /* Buttons - Linear style */
    .stButton > button {
        background: var(--primary);
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 500;
        transition: all 0.15s ease;
    }

    .stButton > button:hover {
        background: var(--primary-hover);
    }

    .stButton > button:active {
        background: var(--primary-focus);
    }

    /* Secondary Button */
    .stButton > button[kind="secondary"] {
        background: var(--surface-1);
        color: var(--ink);
        border: 1px solid var(--hairline);
    }

    .stButton > button[kind="secondary"]:hover {
        border-color: var(--hairline-strong);
    }

    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--surface-1);
        color: var(--ink);
        border: 1px solid var(--hairline);
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 0.875rem;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-focus);
        box-shadow: 0 0 0 2px rgba(94, 106, 210, 0.3);
    }

    /* Select Box */
    .stSelectbox > div > div {
        background: var(--surface-1);
        color: var(--ink);
        border: 1px solid var(--hairline);
        border-radius: 8px;
    }

    /* Radio Buttons */
    .stRadio > div {
        background: var(--surface-1);
        border: 1px solid var(--hairline);
        border-radius: 8px;
        padding: 4px;
    }

    .stRadio > div > label {
        background: transparent;
        color: var(--ink-muted);
        border-radius: 6px;
        padding: 6px 12px;
    }

    .stRadio > div > label[data-checked="true"] {
        background: var(--surface-2);
        color: var(--ink);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: var(--surface-1);
        border: 1px solid var(--hairline);
        border-radius: 8px;
        color: var(--ink);
    }

    .streamlit-expanderContent {
        background: var(--surface-1);
        border: 1px solid var(--hairline);
        border-top: none;
        border-radius: 0 0 8px 8px;
    }

    /* Dataframe */
    .stDataFrame {
        border: 1px solid var(--hairline);
        border-radius: 8px;
        overflow: hidden;
    }

    /* Success/Error Messages */
    .stSuccess {
        background: rgba(39, 166, 68, 0.1);
        border: 1px solid rgba(39, 166, 68, 0.2);
        color: var(--success);
        border-radius: 8px;
    }

    .stError {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border-radius: 8px;
    }

    .stWarning {
        background: rgba(234, 179, 8, 0.1);
        border: 1px solid rgba(234, 179, 8, 0.2);
        color: #eab308;
        border-radius: 8px;
    }

    .stInfo {
        background: rgba(94, 106, 210, 0.1);
        border: 1px solid rgba(94, 106, 210, 0.2);
        color: var(--primary);
        border-radius: 8px;
    }

    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: var(--hairline);
        margin: 2rem 0;
    }

    /* Chat Messages */
    .stChatMessage {
        background: var(--surface-1);
        border: 1px solid var(--hairline);
        border-radius: 12px;
        padding: 16px;
    }

    /* File Uploader */
    .stFileUploader {
        background: var(--surface-1);
        border: 2px dashed var(--hairline-strong);
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
    }

    .stFileUploader:hover {
        border-color: var(--primary);
    }

    /* Metric */
    [data-testid="stMetric"] {
        background: var(--surface-1);
        border: 1px solid var(--hairline);
        border-radius: 8px;
        padding: 16px;
    }

    [data-testid="stMetric"] label {
        color: var(--ink-subtle) !important;
        font-size: 0.75rem !important;
    }

    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: var(--ink) !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--surface-1);
        border-radius: 8px;
        padding: 4px;
        border: 1px solid var(--hairline);
    }

    .stTabs [data-baseweb="tab"] {
        color: var(--ink-subtle);
        border-radius: 6px;
    }

    .stTabs [aria-selected="true"] {
        color: var(--ink);
        background: var(--surface-2);
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--canvas);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--hairline-strong);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--ink-tertiary);
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 标准限值
# ============================================================

STANDARD_LIMITS = {
    "混凝土抗压强度": {
        "C20": {"min": 20.0}, "C25": {"min": 25.0}, "C30": {"min": 30.0},
        "C35": {"min": 35.0}, "C40": {"min": 40.0}, "C45": {"min": 45.0}, "C50": {"min": 50.0},
    },
    "钢筋屈服强度": {
        "HRB400": {"min": 400.0, "max": 540.0},
        "HRB500": {"min": 500.0, "max": 630.0},
    },
    "钢筋抗拉强度": {
        "HRB400": {"min": 540.0},
        "HRB500": {"min": 630.0},
    },
    "坍落度": {
        "普通": {"min": 70.0, "max": 180.0},
        "泵送": {"min": 120.0, "max": 220.0},
    },
}


def check_compliance(indicator_type, value, standard="", spec=None):
    """检查指标合格性"""
    result = {"indicator": indicator_type, "value": value, "standard": standard, "is_compliant": True, "details": ""}
    if spec:
        if "min" in spec and value < spec["min"]:
            result["is_compliant"] = False
            result["details"] = f"检测值 {value} 低于最低要求 {spec['min']}"
        if "max" in spec and value > spec["max"]:
            result["is_compliant"] = False
            result["details"] = f"检测值 {value} 超过最高限值 {spec['max']}"
        if result["is_compliant"]:
            result["details"] = "合格"
        return result
    if indicator_type in STANDARD_LIMITS:
        limits = STANDARD_LIMITS[indicator_type]
        if standard in limits:
            limit = limits[standard]
            if "min" in limit and value < limit["min"]:
                result["is_compliant"] = False
                result["details"] = f"检测值 {value} 低于{standard}最低要求 {limit['min']}"
            if "max" in limit and value > limit["max"]:
                result["is_compliant"] = False
                result["details"] = f"检测值 {value} 超过{standard}最高限值 {limit['max']}"
            if result["is_compliant"]:
                result["details"] = f"符合{standard}标准要求"
        else:
            result["details"] = f"未找到{standard}的限值标准，无法自动判定"
    else:
        result["details"] = f"未找到{indicator_type}的限值标准，需人工判定"
    return result


def analyze_trend(data, indicator_type=""):
    """趋势分析"""
    if not data:
        return {"error": "数据为空"}
    values = [d["value"] for d in data]
    arr = np.array(values)
    result = {
        "indicator_type": indicator_type, "count": len(values),
        "statistics": {
            "mean": float(np.mean(arr)), "std": float(np.std(arr)),
            "min": float(np.min(arr)), "max": float(np.max(arr)),
            "median": float(np.median(arr)),
            "cv": float(np.std(arr) / np.mean(arr) * 100) if np.mean(arr) != 0 else 0,
        },
        "trend": "", "warning": "",
    }
    if len(values) >= 3:
        x = np.arange(len(values))
        coeffs = np.polyfit(x, arr, 1)
        slope = coeffs[0]
        if slope > 0.1:
            result["trend"] = "上升趋势"
        elif slope < -0.1:
            result["trend"] = "下降趋势"
            result["warning"] = "检测值呈下降趋势，需关注质量风险"
        else:
            result["trend"] = "相对稳定"
    cv = result["statistics"]["cv"]
    if cv > 15:
        result["warning"] = (result.get("warning", "") + " " if result.get("warning") else "") + f"变异系数({cv:.1f}%)较大，数据离散程度高"
    return result


def generate_trend_chart(data, title="检测数据趋势图", indicator_name="检测值", unit="", standard_value=None):
    """生成趋势图 - Linear style"""
    dates = [d.get("date", f"样本{i+1}") for i, d in enumerate(data)]
    values = [d["value"] for d in data]
    fig, ax = plt.subplots(figsize=(10, 5), facecolor='#0f1011')
    ax.set_facecolor('#0f1011')

    # Plot with Linear-style colors
    ax.plot(dates, values, color='#5e6ad2', linewidth=2, markersize=6, markerfacecolor='#5e6ad2', label=indicator_name)
    mean_val = np.mean(values)
    ax.axhline(y=mean_val, color='#27a644', linestyle='--', alpha=0.7, label=f'均值: {mean_val:.1f}')
    if standard_value is not None:
        ax.axhline(y=standard_value, color='#ef4444', linestyle='-', alpha=0.7, label=f'标准值: {standard_value}')

    ax.set_title(title, fontsize=14, color='#f7f8f8', fontweight=600, pad=15)
    ax.set_xlabel("日期", fontsize=12, color='#8a8f98')
    ylabel = f"{indicator_name}({unit})" if unit else indicator_name
    ax.set_ylabel(ylabel, fontsize=12, color='#8a8f98')

    # Style the axes
    ax.tick_params(colors='#8a8f98', labelsize=10)
    ax.spines['bottom'].set_color('#23252a')
    ax.spines['left'].set_color('#23252a')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.legend(loc='best', facecolor='#141516', edgecolor='#23252a', labelcolor='#f7f8f8')
    ax.grid(True, alpha=0.1, color='#23252a')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='#0f1011')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64


def generate_distribution_chart(values, title="检测值分布图", indicator_name="检测值", unit="", bins=10):
    """生成分布图 - Linear style"""
    fig, ax = plt.subplots(figsize=(8, 5), facecolor='#0f1011')
    ax.set_facecolor('#0f1011')

    ax.hist(values, bins=bins, color='#5e6ad2', edgecolor='#0f1011', alpha=0.8)
    mean_val = np.mean(values)
    ax.axvline(x=mean_val, color='#ef4444', linestyle='--', label=f'均值: {mean_val:.1f}')

    ax.set_title(title, fontsize=14, color='#f7f8f8', fontweight=600, pad=15)
    xlabel = f"{indicator_name}({unit})" if unit else indicator_name
    ax.set_xlabel(xlabel, fontsize=12, color='#8a8f98')
    ax.set_ylabel("频次", fontsize=12, color='#8a8f98')

    ax.tick_params(colors='#8a8f98', labelsize=10)
    ax.spines['bottom'].set_color('#23252a')
    ax.spines['left'].set_color('#23252a')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.legend(facecolor='#141516', edgecolor='#23252a', labelcolor='#f7f8f8')
    ax.grid(True, alpha=0.1, color='#23252a', axis='y')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='#0f1011')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64


def demo_answer(question):
    """演示模式问答"""
    q = question.lower()

    if any(k in q for k in ["混凝土", "强度", "抗压", "c30", "c35", "c40", "试块"]):
        nums = re.findall(r'[\d.]+', q)
        if "合格" in q or "是否" in q:
            if nums:
                val = float(nums[0])
                grade = "C30"
                for g in ["C20", "C25", "C30", "C35", "C40", "C45", "C50"]:
                    if g.lower() in q:
                        grade = g
                        break
                std_val = int(grade[1:])
                if val >= std_val:
                    return f"检测值 {val}MPa ≥ 设计强度 {grade}({std_val}MPa)\n\n**判定结论：合格** ✅\n\n依据 GB/T 50107-2010《混凝土强度检验评定标准》，该批次混凝土强度满足 {grade} 设计要求。"
                else:
                    return f"检测值 {val}MPa < 设计强度 {grade}({std_val}MPa)\n\n**判定结论：不合格** ❌\n\n依据 GB/T 50107-2010，该批次混凝土强度不满足 {grade} 要求。\n\n**建议措施：**\n1. 进行回弹法或钻芯法复检\n2. 查找强度不足原因（配合比、养护条件等）\n3. 必要时进行结构安全性评估"
        if "评定" in q or "标准" in q:
            return "**混凝土强度评定标准 (GB/T 50107-2010)**\n\n**统计法评定 (n≥10)：**\n1. mfcu - λ₁×Sfcu ≥ fcu,k\n2. fcu,min ≥ λ₂×fcu,k\n\n**非统计法评定 (n<10)：**\n1. mfcu ≥ 1.15×fcu,k\n2. fcu,min ≥ 0.95×fcu,k"
        return "**混凝土强度检测要点：**\n\n- 标准养护条件：温度20±2℃，湿度≥95%\n- 标准龄期：28天\n- 试件尺寸：150mm立方体\n- 依据标准：GB/T 50081, GB/T 50107"

    if any(k in q for k in ["钢筋", "hrb", "屈服", "抗拉"]):
        if "hrb400" in q:
            return "**HRB400钢筋力学性能要求 (GB/T 1499.2-2018)**\n\n| 指标 | 标准要求 |\n|------|----------|\n| 屈服强度 ReL | ≥400 MPa |\n| 抗拉强度 Rm | ≥540 MPa |\n| 强屈比 Rm/ReL | ≥1.25 |\n| 超屈比 ReL实测/400 | ≤1.30 |"
        if "取样" in q or "频率" in q:
            return "**钢筋取样规定 (GB/T 1499.2-2018)**\n\n**组批规则：** 同一牌号、炉罐号、规格、交货状态为一批，每批≤60t\n\n**取样数量：**\n- 拉伸试验：每批2根\n- 弯曲试验：每批2根\n- 重量偏差：每批5根（长度≥500mm）"
        return "**钢筋检测要点：**\n\n- 取样标准：GB/T 1499.2-2018\n- 每批≤60t，取拉伸2根+弯曲2根\n- 检测项目：屈服强度、抗拉强度、伸长率、弯曲\n- 常用牌号：HRB400, HRB500"

    if any(k in q for k in ["回弹", "碳化"]):
        return "**回弹法检测要点 (JGJ/T 23-2011)**\n\n**测区布置：**\n- 每个构件≥10个测区\n- 测区间距≤2m\n- 距构件边缘≥0.2m\n\n**测点要求：**\n- 每测区16个测点\n- 测点间距≥20mm\n\n**碳化深度修正：**\n- 用酚酞试剂测量碳化深度\n- 碳化使表面硬度增加，回弹值偏高"

    if any(k in q for k in ["坍落", "流动性", "工作性"]):
        return "**混凝土坍落度检测 (GB/T 50080)**\n\n**检测步骤：**\n1. 润湿坍落度筒及底板\n2. 将混凝土分三层装入筒内\n3. 每层用捣棒插捣25次\n4. 刮平顶面\n5. 5-10秒内垂直提起筒\n6. 测量筒顶与坍落后混凝土最高点的高度差\n\n**常用范围：**\n- 普通混凝土：70-180mm\n- 泵送混凝土：120-220mm"

    if any(k in q for k in ["桩基", "桩", "静载", "高应变", "低应变"]):
        return "**桩基检测方法 (JGJ 106-2014)**\n\n| 方法 | 检测内容 | 数量要求 |\n|------|---------|----------|\n| 静载试验 | 承载力 | 1%且≥3根 |\n| 高应变法 | 承载力+完整性 | 5%且≥5根 |\n| 低应变法 | 完整性 | 20%且≥10根 |\n| 声波透射法 | 完整性 | 10%且≥10根 |"

    if any(k in q for k in ["标准", "规范", "gb", "jgj", "条文"]):
        return "**常用工程质量标准：**\n\n- GB/T 50107 混凝土强度检验评定标准\n- GB 50204 混凝土结构工程施工质量验收规范\n- GB/T 50081 混凝土力学性能试验方法标准\n- GB/T 228.1 金属材料拉伸试验\n- GB/T 1499.2 钢筋混凝土用钢\n- JGJ/T 23 回弹法检测混凝土抗压强度技术规程\n\n请提出具体问题，我会为您解答。"

    return "我是「智检通」工程质量检测分析助手，可以帮您：\n\n1. **分析检测报告** - 上传PDF自动解析\n2. **查询标准规范** - 如「混凝土强度评定标准是什么」\n3. **分析数据趋势** - 检测数据的统计分析\n4. **生成检测报告** - 自动生成规范报告\n\n请告诉我您需要什么帮助？"


# ============================================================
# 页面渲染函数
# ============================================================

def render_home():
    """首页 - Linear style hero layout"""
    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">工程质量检测智能分析系统</div>
        <h1 class="display-xl">智检通</h1>
        <p class="body-lg" style="max-width: 600px; margin: 1.5rem auto 0;">
            基于大模型Agent的工程质量检测全流程智能分析平台<br>
            让检测更高效、更精准、更智能
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Feature Cards
    st.markdown('<p class="eyebrow" style="margin-bottom: 1.5rem;">核心功能</p>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="icon">📊</div>
            <h3>报告分析</h3>
            <p>自动解析检测报告PDF，提取关键指标，智能判定合格性</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="icon">📚</div>
            <h3>标准问答</h3>
            <p>基于RAG的工程质量标准智能检索与精准问答</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="icon">📈</div>
            <h3>趋势分析</h3>
            <p>检测数据时间序列分析，识别趋势和异常波动</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="icon">📝</div>
            <h3>报告生成</h3>
            <p>根据检测数据自动生成规范化质量检测报告</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Architecture Section
    st.markdown('<p class="eyebrow" style="margin-bottom: 1.5rem;">系统架构</p>', unsafe_allow_html=True)

    # 系统架构图片
    st.image("assets/architecture.png", use_container_width=True, caption="系统架构图")

    st.markdown("<br>", unsafe_allow_html=True)

    # 技术栈
    st.markdown('<p class="eyebrow" style="margin-bottom: 1rem;">技术栈</p>', unsafe_allow_html=True)
    techs = ["Qwen2.5-7B", "QLoRA微调", "多Agent协同", "Milvus向量库", "Streamlit", "RAG检索增强"]
    cols = st.columns(6)
    for i, tech in enumerate(techs):
        with cols[i]:
            st.markdown(f"""
            <div style="background: #141516; border: 1px solid #23252a; border-radius: 8px; padding: 12px; text-align: center;">
                <span class="tech-tag" style="margin: 0;">{tech}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Footer Info
    st.markdown("""
    <div class="surface-card" style="text-align: center;">
        <p class="body-sm" style="margin: 0;">
            <strong>说明：</strong>当前为演示版本，使用基于规则的智能回复。完整版本支持本地大模型推理和RAG知识库检索。<br>
            <strong>参赛信息：</strong>第二届武汉理工大学中国研究生智能建造创新大赛 · 工程大模型 Agent 智能应用系统设计赛道<br>
            <strong>参赛人员：</strong>吴武俊
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_report_analysis():
    """报告分析页面"""
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 class="display-md">检测报告分析</h1>
        <p class="body">上传工程质量检测报告PDF文件，系统将自动解析并分析检测结果。</p>
    </div>
    """, unsafe_allow_html=True)

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

            st.markdown('<p class="eyebrow">报告信息</p>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("文件名", uploaded_file.name)
            with col2:
                st.metric("页数", len(reader.pages))
            with col3:
                st.metric("字符数", len(full_text))

            # 提取指标
            indicators = []
            pattern = r"(?:抗压强度|压力)[：:]\s*([\d.]+)\s*(?:MPa|mpa|兆帕)"
            for match in re.finditer(pattern, full_text):
                indicators.append({"type": "混凝土抗压强度", "value": float(match.group(1)), "unit": "MPa"})

            pattern = r"(?:屈服强度|抗拉强度)[：:]\s*([\d.]+)\s*(?:MPa|mpa)"
            for match in re.finditer(pattern, full_text):
                name = "屈服强度" if "屈服" in match.group(0) else "抗拉强度"
                indicators.append({"type": f"钢筋{name}", "value": float(match.group(1)), "unit": "MPa"})

            pattern = r"坍落度[：:]\s*([\d.]+)\s*(?:mm|毫米)"
            for match in re.finditer(pattern, full_text):
                indicators.append({"type": "坍落度", "value": float(match.group(1)), "unit": "mm"})

            if indicators:
                st.markdown('<p class="eyebrow" style="margin-top: 2rem;">检测指标分析</p>', unsafe_allow_html=True)
                for i, ind in enumerate(indicators):
                    compliance = check_compliance(ind["type"], ind["value"], "C30")
                    status_class = "status-badge-success" if compliance["is_compliant"] else "status-badge-error"
                    status_text = "合格" if compliance["is_compliant"] else "不合格"

                    with st.expander(f"{ind['type']}: {ind['value']}{ind.get('unit', '')}"):
                        if compliance["is_compliant"]:
                            st.success(f"✅ {compliance['details']}")
                        else:
                            st.error(f"❌ {compliance['details']}")

                st.markdown('<p class="eyebrow" style="margin-top: 2rem;">综合分析结论</p>', unsafe_allow_html=True)
                all_compliant = all(check_compliance(ind["type"], ind["value"], "C30")["is_compliant"] for ind in indicators)
                if all_compliant:
                    st.success("✅ 该报告所有检测指标均符合标准要求")
                else:
                    st.warning("⚠️ 部分检测指标不符合标准要求，请查看详情")
            else:
                st.warning("未能从报告中提取到检测指标，请检查报告格式")

            with st.expander("查看报告原始文本"):
                st.text_area("", full_text[:5000], height=300)
        except Exception as e:
            st.error(f"解析失败: {e}")
    else:
        st.markdown("""
        <div class="surface-card">
            <h3 class="card-title">使用说明</h3>
            <p class="body">
                1. 上传PDF格式的工程质量检测报告<br>
                2. 系统自动解析报告内容<br>
                3. 提取关键检测指标（混凝土强度、钢筋性能等）<br>
                4. 对照标准进行合格性判定<br>
                5. 生成分析结论
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="margin-top: 1.5rem;">
            <p class="eyebrow">支持的报告类型</p>
            <div style="display: flex; gap: 1rem; margin-top: 0.5rem;">
                <span class="tech-tag">混凝土抗压强度检测报告</span>
                <span class="tech-tag">钢筋力学性能检测报告</span>
                <span class="tech-tag">混凝土坍落度检测报告</span>
                <span class="tech-tag">回弹法检测报告</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<p class="eyebrow" style="margin-top: 2rem;">演示数据</p>', unsafe_allow_html=True)
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


def render_standard_qa():
    """标准问答页面"""
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 class="display-md">工程质量标准问答</h1>
        <p class="body">基于RAG知识库的工程质量标准智能检索与问答系统</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if "qa_messages" not in st.session_state:
        st.session_state.qa_messages = []

    for msg in st.session_state.qa_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.markdown('<p class="eyebrow">常见问题</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("混凝土强度评定标准是什么？", use_container_width=True):
            q = "混凝土强度评定标准是什么？依据哪个规范？"
            st.session_state.qa_messages.append({"role": "user", "content": q})
            answer = demo_answer(q)
            st.session_state.qa_messages.append({"role": "assistant", "content": answer})
            st.rerun()
        if st.button("钢筋取样频率规定？", use_container_width=True):
            q = "钢筋力学性能检测的取样频率和数量是如何规定的？"
            st.session_state.qa_messages.append({"role": "user", "content": q})
            answer = demo_answer(q)
            st.session_state.qa_messages.append({"role": "assistant", "content": answer})
            st.rerun()
    with col2:
        if st.button("回弹法检测注意事项？", use_container_width=True):
            q = "回弹法检测混凝土强度时需要注意哪些事项？"
            st.session_state.qa_messages.append({"role": "user", "content": q})
            answer = demo_answer(q)
            st.session_state.qa_messages.append({"role": "assistant", "content": answer})
            st.rerun()
        if st.button("坍落度检测方法？", use_container_width=True):
            q = "混凝土坍落度的检测方法和步骤是什么？"
            st.session_state.qa_messages.append({"role": "user", "content": q})
            answer = demo_answer(q)
            st.session_state.qa_messages.append({"role": "assistant", "content": answer})
            st.rerun()

    user_input = st.chat_input("请输入关于工程质量标准的问题...")
    if user_input:
        st.session_state.qa_messages.append({"role": "user", "content": user_input})
        answer = demo_answer(user_input)
        st.session_state.qa_messages.append({"role": "assistant", "content": answer})
        st.rerun()


def render_trend_analysis():
    """趋势分析页面"""
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 class="display-md">检测数据趋势分析</h1>
        <p class="body">分析检测数据的时间趋势，识别异常波动和质量风险</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    input_method = st.radio("数据输入方式", ["手动输入", "使用演示数据"], horizontal=True)
    data = []

    if input_method == "手动输入":
        st.markdown('<p class="eyebrow">输入检测数据</p>', unsafe_allow_html=True)
        num_samples = st.number_input("样本数量", min_value=3, max_value=100, value=10)
        data = []
        for i in range(num_samples):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input(f"日期 {i+1}", value=datetime.now() - timedelta(days=num_samples - i), key=f"date_{i}")
            with col2:
                value = st.number_input(f"检测值 {i+1}", min_value=0.0, value=30.0 + np.random.normal(0, 2), key=f"value_{i}")
            data.append({"date": date.strftime("%Y-%m-%d"), "value": value})
    else:
        np.random.seed(42)
        dates = [(datetime.now() - timedelta(days=30 - i)).strftime("%Y-%m-%d") for i in range(30)]
        values = [30 + np.random.normal(0, 2) + 0.05 * i for i in range(30)]
        data = [{"date": d, "value": v} for d, v in zip(dates, values)]
        st.markdown('<p class="eyebrow">演示数据 (混凝土抗压强度)</p>', unsafe_allow_html=True)
        st.dataframe(data, use_container_width=True)

    if data:
        indicator_type = st.selectbox("选择检测指标", ["混凝土抗压强度", "钢筋屈服强度", "坍落度", "回弹值"])
        st.markdown("---")
        st.markdown('<p class="eyebrow">分析结果</p>', unsafe_allow_html=True)

        result = analyze_trend(data, indicator_type)
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

        unit_map = {"混凝土抗压强度": "MPa", "钢筋屈服强度": "MPa", "坍落度": "mm", "回弹值": ""}
        st.markdown('<p class="eyebrow" style="margin-top: 2rem;">趋势图</p>', unsafe_allow_html=True)
        chart_base64 = generate_trend_chart(data, title=f"{indicator_type}趋势图", indicator_name=indicator_type, unit=unit_map.get(indicator_type, ""))
        st.image(io.BytesIO(base64.b64decode(chart_base64)), use_container_width=True)

        st.markdown('<p class="eyebrow" style="margin-top: 2rem;">分布图</p>', unsafe_allow_html=True)
        values = [d["value"] for d in data]
        dist_base64 = generate_distribution_chart(values, title=f"{indicator_type}分布图", indicator_name=indicator_type, unit=unit_map.get(indicator_type, ""))
        st.image(io.BytesIO(base64.b64decode(dist_base64)), use_container_width=True)

        if result.get("warning"):
            st.warning(f"⚠️ {result['warning']}")

        st.markdown('<p class="eyebrow" style="margin-top: 2rem;">数据明细</p>', unsafe_allow_html=True)
        st.dataframe(data, use_container_width=True)


def render_report_generate():
    """报告生成页面"""
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 class="display-md">检测报告生成</h1>
        <p class="body">根据检测数据自动生成规范的质量检测报告</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<p class="eyebrow">报告基本信息</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        project_name = st.text_input("工程名称", "XX住宅小区一期工程")
        client = st.text_input("委托单位", "XX建设集团有限公司")
        test_unit = st.text_input("检测单位", "XX工程质量检测中心")
    with col2:
        report_id = st.text_input("报告编号", f"JC-{datetime.now().strftime('%Y%m%d')}")
        test_date = st.date_input("检测日期", datetime.now())
        report_date = st.date_input("报告日期", datetime.now())

    st.markdown('<p class="eyebrow" style="margin-top: 2rem;">检测项目</p>', unsafe_allow_html=True)
    num_items = st.number_input("检测项目数量", min_value=1, max_value=20, value=3)
    test_items = []
    for i in range(num_items):
        st.markdown(f"**项目 {i+1}**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            item_type = st.selectbox("检测项目", ["混凝土抗压强度", "钢筋屈服强度", "钢筋抗拉强度", "坍落度", "回弹值"], key=f"type_{i}")
        with col2:
            value = st.number_input("检测值", min_value=0.0, value=30.0, key=f"value_{i}")
        with col3:
            unit_map = {"混凝土抗压强度": "MPa", "钢筋屈服强度": "MPa", "钢筋抗拉强度": "MPa", "坍落度": "mm", "回弹值": ""}
            st.text_input("单位", unit_map.get(item_type, ""), key=f"unit_{i}", disabled=True)
        with col4:
            standard = st.text_input("标准/等级", "C30", key=f"standard_{i}")

        result = check_compliance(item_type, value, standard)
        test_items.append({"name": item_type, "value": value, "unit": unit_map.get(item_type, ""), "standard": standard, "is_compliant": result["is_compliant"]})

    st.markdown('<p class="eyebrow" style="margin-top: 2rem;">检测依据</p>', unsafe_allow_html=True)
    standards = st.text_area("检测依据标准", "1. GB/T 50107-2010 混凝土强度检验评定标准\n2. GB 50204-2015 混凝土结构工程施工质量验收规范\n3. GB/T 1499.2-2018 钢筋混凝土用钢 第2部分：热轧带肋钢筋", height=150)

    project_desc = st.text_area("工程概况", "根据委托方要求，对本工程相关材料/构件进行质量检测。", height=100)
    output_format = st.radio("输出格式", ["markdown", "text"], horizontal=True)

    st.markdown("---")
    if st.button("生成报告", type="primary", use_container_width=True):
        now = datetime.now().strftime("%Y-%m-%d")
        all_pass = all(item.get("is_compliant", True) for item in test_items)
        if all_pass:
            conclusion = "经检测，所检项目均符合相关标准要求。"
        else:
            failed_items = [item["name"] for item in test_items if not item.get("is_compliant", True)]
            conclusion = f"经检测，以下项目不符合标准要求: {', '.join(failed_items)}。建议进行复检或采取相应处理措施。"

        if output_format == "markdown":
            test_results = "| 序号 | 检测项目 | 检测值 | 单位 | 标准要求 | 判定 |\n|------|---------|--------|------|---------|------|\n"
            for i, item in enumerate(test_items, 1):
                status = "合格" if item.get("is_compliant", True) else "不合格"
                test_results += f"| {i} | {item['name']} | {item['value']} | {item.get('unit', '')} | {item.get('standard', '-')} | {status} |\n"

            report_content = f"""# 质量检测报告

| 项目 | 内容 |
|------|------|
| 报告编号 | {report_id} |
| 工程名称 | {project_name} |
| 委托单位 | {client} |
| 检测日期 | {test_date} |
| 报告日期 | {report_date} |

## 一、工程概况

{project_desc}

## 二、检测依据

{standards}

## 三、检测项目及结果

{test_results}

## 四、检测结论

{conclusion}

---

检测单位: {test_unit}
报告日期: {report_date}
"""
            st.markdown('<p class="eyebrow">生成的报告</p>', unsafe_allow_html=True)
            st.markdown(report_content)
        else:
            lines = []
            for i, item in enumerate(test_items, 1):
                status = "合格" if item.get("is_compliant", True) else "不合格"
                lines.append(f"  {i}. {item['name']}: {item['value']}{item.get('unit', '')} [{status}]")
            test_results = "\n".join(lines)

            report_content = f"""质量检测报告
{'='*50}

报告编号: {report_id}
工程名称: {project_name}
委托单位: {client}
检测日期: {test_date}
报告日期: {report_date}

一、工程概况
{project_desc}

二、检测依据
{standards}

三、检测项目及结果
{test_results}

四、检测结论
{conclusion}

{'='*50}
检测单位: {test_unit}
报告日期: {report_date}
"""
            st.markdown('<p class="eyebrow">生成的报告</p>', unsafe_allow_html=True)
            st.text_area("", report_content, height=600)

        st.download_button(label="下载报告", data=report_content, file_name=f"检测报告_{report_id}.md" if output_format == "markdown" else f"检测报告_{report_id}.txt", mime="text/markdown" if output_format == "markdown" else "text/plain")

        st.markdown('<p class="eyebrow" style="margin-top: 2rem;">合格性统计</p>', unsafe_allow_html=True)
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


# ============================================================
# 主函数
# ============================================================

def main():
    with st.sidebar:
        st.markdown("""
        <div style="padding: 1rem 0;">
            <h2 style="color: #f7f8f8; margin: 0; letter-spacing: -0.6px;">⚡ 智检通</h2>
            <p style="color: #8a8f98; margin: 0.5rem 0 0 0; font-size: 0.875rem;">工程质量检测智能分析</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        page = st.radio("功能导航", ["首页", "报告分析", "标准问答", "趋势分析", "报告生成"], index=0)

        st.markdown("---")
        st.markdown("""
        <div style="background: #141516; padding: 12px; border-radius: 8px; border: 1px solid #23252a;">
            <p style="color: #8a8f98; margin: 0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.4px;">系统状态</p>
            <p style="color: #27a644; margin: 4px 0 0 0; font-size: 0.875rem;">✓ 就绪（演示模式）</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="margin-top: 1rem; background: #141516; padding: 12px; border-radius: 8px; border: 1px solid #23252a;">
            <p style="color: #8a8f98; margin: 0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.4px;">参赛信息</p>
            <p style="color: #d0d6e0; margin: 4px 0 0 0; font-size: 0.8125rem;">
                工程大模型 Agent<br>智能应用系统设计赛道<br>武汉理工大学<br>参赛人员：吴武俊
            </p>
        </div>
        """, unsafe_allow_html=True)

    if page == "首页":
        render_home()
    elif page == "报告分析":
        render_report_analysis()
    elif page == "标准问答":
        render_standard_qa()
    elif page == "趋势分析":
        render_trend_analysis()
    elif page == "报告生成":
        render_report_generate()


if __name__ == "__main__":
    main()
