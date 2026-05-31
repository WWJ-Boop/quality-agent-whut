"""报告撰写工具

根据检测数据自动生成规范的检测报告。
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


REPORT_TEMPLATE = """
质量检测报告
{'='*50}

报告编号: {report_id}
工程名称: {project_name}
委托单位: {client}
检测日期: {date}
报告日期: {report_date}

一、工程概况
{project_desc}

二、检测依据
{standards}

三、检测项目及结果
{test_results}

四、检测结论
{conclusion}

五、备注
{remarks}

{'='*50}
检测单位: {test_unit}
审核人: {reviewer}
批准人: {approver}
报告日期: {report_date}
"""


def generate_report(
    report_data: dict,
    output_format: str = "text",
) -> str:
    """生成检测报告

    Args:
        report_data: 报告数据字典
        output_format: 输出格式 ("text" / "markdown")

    Returns:
        报告文本内容
    """
    now = datetime.now().strftime("%Y-%m-%d")

    report_id = report_data.get("report_id", f"JC-{datetime.now().strftime('%Y%m%d%H%M%S')}")
    project_name = report_data.get("project_name", "未命名工程")
    client = report_data.get("client", "未填写")
    date = report_data.get("date", now)
    project_desc = report_data.get("project_desc", "根据委托方要求，对本工程相关材料/构件进行质量检测。")
    standards = report_data.get("standards", "依据相关国家标准及行业规范进行检测。")

    # 生成检测结果表格
    test_items = report_data.get("test_items", [])
    test_results = _format_test_results(test_items, output_format)

    # 生成结论
    all_pass = all(item.get("is_compliant", True) for item in test_items) if test_items else True
    if all_pass:
        conclusion = "经检测，所检项目均符合相关标准要求。"
    else:
        failed_items = [item["name"] for item in test_items if not item.get("is_compliant", True)]
        conclusion = f"经检测，以下项目不符合标准要求: {', '.join(failed_items)}。建议进行复检或采取相应处理措施。"

    if output_format == "markdown":
        return _generate_markdown_report(
            report_id, project_name, client, date, now,
            project_desc, standards, test_results, conclusion,
            report_data,
        )
    else:
        return REPORT_TEMPLATE.format(
            report_id=report_id,
            project_name=project_name,
            client=client,
            date=date,
            report_date=now,
            project_desc=project_desc,
            standards=standards,
            test_results=test_results,
            conclusion=conclusion,
            remarks=report_data.get("remarks", "无"),
            test_unit=report_data.get("test_unit", "XX检测中心"),
            reviewer=report_data.get("reviewer", ""),
            approver=report_data.get("approver", ""),
        )


def _format_test_results(test_items: List[dict], fmt: str = "text") -> str:
    """格式化检测结果"""
    if not test_items:
        return "暂无检测数据。"

    if fmt == "markdown":
        lines = ["| 序号 | 检测项目 | 检测值 | 单位 | 标准要求 | 判定 |",
                 "|------|---------|--------|------|---------|------|"]
        for i, item in enumerate(test_items, 1):
            status = "合格" if item.get("is_compliant", True) else "不合格"
            standard = item.get("standard", "-")
            lines.append(f"| {i} | {item['name']} | {item['value']} | {item.get('unit', '')} | {standard} | {status} |")
        return "\n".join(lines)
    else:
        lines = []
        for i, item in enumerate(test_items, 1):
            status = "合格" if item.get("is_compliant", True) else "不合格"
            lines.append(f"  {i}. {item['name']}: {item['value']}{item.get('unit', '')} [{status}]")
        return "\n".join(lines)


def _generate_markdown_report(
    report_id, project_name, client, date, report_date,
    project_desc, standards, test_results, conclusion, report_data,
) -> str:
    """生成Markdown格式报告"""
    return f"""# 质量检测报告

| 项目 | 内容 |
|------|------|
| 报告编号 | {report_id} |
| 工程名称 | {project_name} |
| 委托单位 | {client} |
| 检测日期 | {date} |
| 报告日期 | {report_date} |

## 一、工程概况

{project_desc}

## 二、检测依据

{standards}

## 三、检测项目及结果

{test_results}

## 四、检测结论

{conclusion}

## 五、备注

{report_data.get('remarks', '无')}

---

检测单位: {report_data.get('test_unit', 'XX检测中心')}
审核人: {report_data.get('reviewer', '')}
批准人: {report_data.get('approver', '')}
"""
