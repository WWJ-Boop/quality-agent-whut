"""训练数据准备脚本

将JSONL格式的训练数据转换为LLaMA-Factory所需的格式。
"""

import json
import sys
from pathlib import Path

# 将项目根目录加入路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def load_jsonl(file_path: str) -> list:
    """加载JSONL文件"""
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def convert_to_llamafactory_format(data: list) -> list:
    """转换为LLaMA-Factory训练格式

    LLaMA-Factory格式:
    {
        "instruction": "用户指令",
        "input": "可选输入",
        "output": "期望输出",
        "system": "系统提示词（可选）"
    }
    """
    formatted = []
    system_prompt = "你是"智检通"工程质量检测分析助手，精通各类工程质量标准和检测方法。请用专业、准确的方式回答问题。"

    for item in data:
        formatted_item = {
            "instruction": item.get("instruction", item.get("question", "")),
            "input": item.get("input", ""),
            "output": item.get("output", item.get("answer", "")),
            "system": system_prompt,
        }
        formatted.append(formatted_item)

    return formatted


def save_dataset(data: list, output_path: str):
    """保存为JSON文件"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已保存 {len(data)} 条数据到 {output_path}")


def main():
    base_dir = Path(__file__).parent.parent.parent / "data" / "training"

    # 处理训练集
    train_data = load_jsonl(str(base_dir / "train.jsonl"))
    train_formatted = convert_to_llamafactory_format(train_data)
    save_dataset(train_formatted, str(base_dir / "train_formatted.json"))

    # 处理验证集
    val_file = base_dir / "val.jsonl"
    if val_file.exists():
        val_data = load_jsonl(str(val_file))
        val_formatted = convert_to_llamafactory_format(val_data)
        save_dataset(val_formatted, str(base_dir / "val_formatted.json"))

    print(f"\n数据准备完成!")
    print(f"训练集: {len(train_formatted)} 条")
    if val_file.exists():
        print(f"验证集: {len(val_formatted)} 条")

    # 显示示例
    print("\n数据示例:")
    print(json.dumps(train_formatted[0], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
