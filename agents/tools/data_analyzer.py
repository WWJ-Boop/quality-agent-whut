"""数据分析工具

提供检测数据的统计分析和合格性判定。
"""

import json
from typing import List, Dict, Optional
import numpy as np


# 常见检测项目的标准限值
STANDARD_LIMITS = {
    "混凝土抗压强度": {
        "C20": {"min": 20.0},
        "C25": {"min": 25.0},
        "C30": {"min": 30.0},
        "C35": {"min": 35.0},
        "C40": {"min": 40.0},
        "C45": {"min": 45.0},
        "C50": {"min": 50.0},
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


def check_compliance(
    indicator_type: str,
    value: float,
    standard: str = "",
    spec: Optional[dict] = None,
) -> dict:
    """检查单个指标是否合格

    Args:
        indicator_type: 指标类型（如"混凝土抗压强度"）
        value: 检测值
        standard: 标准/等级（如"C30"）
        spec: 自定义限值 {"min": x, "max": y}

    Returns:
        合格判定结果
    """
    result = {
        "indicator": indicator_type,
        "value": value,
        "standard": standard,
        "is_compliant": True,
        "details": "",
    }

    # 使用自定义限值
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

    # 使用内置标准限值
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


def analyze_trend(data: List[dict], indicator_type: str = "") -> dict:
    """分析检测数据趋势

    Args:
        data: 时间序列数据 [{"date": "2024-01", "value": 32.5}, ...]
        indicator_type: 指标类型

    Returns:
        趋势分析结果
    """
    if not data:
        return {"error": "数据为空"}

    values = [d["value"] for d in data]
    dates = [d.get("date", f"样本{i+1}") for i, d in enumerate(data)]

    arr = np.array(values)
    result = {
        "indicator_type": indicator_type,
        "count": len(values),
        "statistics": {
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "median": float(np.median(arr)),
            "cv": float(np.std(arr) / np.mean(arr) * 100) if np.mean(arr) != 0 else 0,
        },
        "trend": "",
        "warning": "",
    }

    # 简单线性趋势分析
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

    # 变异系数分析
    cv = result["statistics"]["cv"]
    if cv > 15:
        result["warning"] = (result.get("warning", "") + " " if result.get("warning") else "") + \
                           f"变异系数({cv:.1f}%)较大，数据离散程度高"

    return result


def batch_check_compliance(indicators: List[dict]) -> List[dict]:
    """批量检查指标合格性

    Args:
        indicators: [{"type": "混凝土抗压强度", "value": 32.5, "standard": "C30"}, ...]
    """
    results = []
    for ind in indicators:
        check_result = check_compliance(
            indicator_type=ind.get("type", ""),
            value=ind.get("value", 0),
            standard=ind.get("standard", ""),
            spec=ind.get("spec"),
        )
        results.append(check_result)
    return results
