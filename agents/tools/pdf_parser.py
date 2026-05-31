"""PDF解析工具

解析工程质量检测报告PDF，提取关键指标数据。
"""

import re
from typing import Dict, List, Optional
from pathlib import Path


def parse_report_pdf(file_path: str) -> dict:
    """解析检测报告PDF文件

    Args:
        file_path: PDF文件路径

    Returns:
        解析结果字典，包含报告基本信息和检测数据
    """
    from PyPDF2 import PdfReader

    path = Path(file_path)
    if not path.exists():
        return {"error": f"文件不存在: {file_path}"}

    reader = PdfReader(str(path))
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    result = {
        "file_name": path.name,
        "total_pages": len(reader.pages),
        "raw_text": full_text,
        "indicators": extract_indicators(full_text),
        "report_info": extract_report_info(full_text),
    }
    return result


def extract_indicators(text: str) -> List[dict]:
    """从文本中提取检测指标

    支持提取:
    - 混凝土抗压强度 (MPa)
    - 钢筋屈服强度/抗拉强度 (MPa)
    - 坍落度 (mm)
    - 回弹值
    - 碳化深度 (mm)
    """
    indicators = []

    # 混凝土抗压强度
    pattern = r"(?:抗压强度|压力)[：:]\s*([\d.]+)\s*(?:MPa|mpa|兆帕)"
    for match in re.finditer(pattern, text):
        indicators.append({
            "type": "混凝土抗压强度",
            "value": float(match.group(1)),
            "unit": "MPa",
            "raw": match.group(0),
        })

    # 钢筋强度
    pattern = r"(?:屈服强度|抗拉强度)[：:]\s*([\d.]+)\s*(?:MPa|mpa)"
    for match in re.finditer(pattern, text):
        name = "屈服强度" if "屈服" in match.group(0) else "抗拉强度"
        indicators.append({
            "type": f"钢筋{name}",
            "value": float(match.group(1)),
            "unit": "MPa",
            "raw": match.group(0),
        })

    # 坍落度
    pattern = r"坍落度[：:]\s*([\d.]+)\s*(?:mm|毫米)"
    for match in re.finditer(pattern, text):
        indicators.append({
            "type": "坍落度",
            "value": float(match.group(1)),
            "unit": "mm",
            "raw": match.group(0),
        })

    # 回弹值
    pattern = r"(?:回弹值|回弹)[：:]\s*([\d.]+)"
    for match in re.finditer(pattern, text):
        indicators.append({
            "type": "回弹值",
            "value": float(match.group(1)),
            "unit": "",
            "raw": match.group(0),
        })

    return indicators


def extract_report_info(text: str) -> dict:
    """提取报告基本信息"""
    info = {}

    # 工程名称
    match = re.search(r"工程名称[：:]\s*(.+?)[\n\r]", text)
    if match:
        info["project_name"] = match.group(1).strip()

    # 委托单位
    match = re.search(r"委托单位[：:]\s*(.+?)[\n\r]", text)
    if match:
        info["client"] = match.group(1).strip()

    # 检测日期
    match = re.search(r"(?:检测日期|报告日期)[：:]\s*([\d\-/.]+)", text)
    if match:
        info["date"] = match.group(1).strip()

    # 报告编号
    match = re.search(r"报告编号[：:]\s*(\S+)", text)
    if match:
        info["report_id"] = match.group(1).strip()

    # 设计强度等级
    match = re.search(r"(?:设计强度|强度等级)[：:]\s*(C\d+)", text)
    if match:
        info["design_strength"] = match.group(1).strip()

    return info
