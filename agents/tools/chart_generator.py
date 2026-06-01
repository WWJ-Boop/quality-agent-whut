"""图表生成工具

生成检测数据的可视化图表。
"""

import io
import base64
from typing import List, Optional
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Zen Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def generate_trend_chart(
    data: List[dict],
    title: str = "检测数据趋势图",
    indicator_name: str = "检测值",
    unit: str = "",
    standard_value: Optional[float] = None,
) -> str:
    """生成趋势折线图

    Args:
        data: [{"date": "2024-01", "value": 32.5}, ...]
        title: 图表标题
        indicator_name: 指标名称
        unit: 单位
        standard_value: 标准值参考线

    Returns:
        base64编码的图片字符串
    """
    dates = [d.get("date", f"样本{i+1}") for i, d in enumerate(data)]
    values = [d["value"] for d in data]

    fig, ax = plt.subplots(figsize=(10, 5))

    # 绘制趋势线
    ax.plot(dates, values, 'b-o', linewidth=2, markersize=6, label=indicator_name)

    # 绘制均值线
    mean_val = np.mean(values)
    ax.axhline(y=mean_val, color='g', linestyle='--', alpha=0.7, label=f'均值: {mean_val:.1f}')

    # 绘制标准值参考线
    if standard_value is not None:
        ax.axhline(y=standard_value, color='r', linestyle='-', alpha=0.7, label=f'标准值: {standard_value}')

    ax.set_title(title, fontsize=14)
    ax.set_xlabel("日期", fontsize=12)
    ylabel = f"{indicator_name}({unit})" if unit else indicator_name
    ax.set_ylabel(ylabel, fontsize=12)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # 转为base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return img_base64


def generate_comparison_chart(
    categories: List[str],
    values: List[float],
    standard_values: Optional[List[float]] = None,
    title: str = "检测值对比图",
    unit: str = "",
) -> str:
    """生成柱状对比图

    Args:
        categories: 类别名称列表
        values: 检测值列表
        standard_values: 标准值列表
        title: 图表标题
        unit: 单位

    Returns:
        base64编码的图片字符串
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.arange(len(categories))
    width = 0.35

    bars1 = ax.bar(x - width/2, values, width, label='检测值', color='steelblue')

    if standard_values:
        bars2 = ax.bar(x + width/2, standard_values, width, label='标准值', color='coral')

    ax.set_title(title, fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()

    if unit:
        ax.set_ylabel(f"数值({unit})", fontsize=12)

    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return img_base64


def generate_distribution_chart(
    values: List[float],
    title: str = "检测值分布图",
    indicator_name: str = "检测值",
    unit: str = "",
    bins: int = 10,
) -> str:
    """生成直方分布图"""
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.hist(values, bins=bins, color='steelblue', edgecolor='white', alpha=0.8)

    mean_val = np.mean(values)
    ax.axvline(x=mean_val, color='r', linestyle='--', label=f'均值: {mean_val:.1f}')

    ax.set_title(title, fontsize=14)
    xlabel = f"{indicator_name}({unit})" if unit else indicator_name
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel("频次", fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return img_base64
