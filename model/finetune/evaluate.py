"""模型评估脚本

评估微调模型在工程质量检测领域的表现。
"""

import json
import sys
from pathlib import Path
from typing import List, Dict

# 将项目根目录加入路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# 评估测试集
EVAL_QUESTIONS = [
    {
        "question": "混凝土试块28天抗压强度检测值为32.5MPa，设计强度等级C30，是否合格？",
        "keywords": ["合格", "GB/T 50107", "30", "满足"],
    },
    {
        "question": "HRB400钢筋的屈服强度标准要求是多少？",
        "keywords": ["400MPa", "≥400", "GB/T 1499.2"],
    },
    {
        "question": "回弹法检测混凝土强度时，碳化深度如何测量？",
        "keywords": ["酚酞", "钻孔", "变色", "碳化深度"],
    },
    {
        "question": "混凝土坍落度检测的步骤是什么？",
        "keywords": ["坍落度筒", "分三层", "插捣", "提起"],
    },
    {
        "question": "桩基静载试验的检测数量是如何规定的？",
        "keywords": ["1%", "≥3根", "总桩数"],
    },
]


def load_model(model_path: str):
    """加载模型"""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    print(f"加载模型: {model_path}")
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    return model, tokenizer


def generate_response(model, tokenizer, question: str, system_prompt: str = "") -> str:
    """生成回答"""
    import torch

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": question})

    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([text], return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=1024,
            temperature=0.1,
            do_sample=True,
            top_p=0.9,
        )

    response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)
    return response


def evaluate_model(model_path: str):
    """评估模型"""
    model, tokenizer = load_model(model_path)

    system_prompt = "你是'智检通'工程质量检测分析助手，精通各类工程质量标准和检测方法。请用专业、准确的方式回答问题。"

    results = []
    total_score = 0

    print("\n开始评估...\n")
    print("=" * 60)

    for i, qa in enumerate(EVAL_QUESTIONS, 1):
        question = qa["question"]
        keywords = qa["keywords"]

        print(f"\n问题 {i}: {question}")
        print("-" * 40)

        response = generate_response(model, tokenizer, question, system_prompt)
        print(f"回答: {response[:200]}...")

        # 检查关键词覆盖
        hit_keywords = [kw for kw in keywords if kw in response]
        score = len(hit_keywords) / len(keywords) * 100
        total_score += score

        print(f"关键词命中: {hit_keywords} ({score:.0f}%)")
        results.append({
            "question": question,
            "response": response,
            "score": score,
            "hit_keywords": hit_keywords,
        })

    avg_score = total_score / len(EVAL_QUESTIONS)
    print("\n" + "=" * 60)
    print(f"\n评估完成! 平均得分: {avg_score:.1f}%")

    # 保存评估结果
    eval_dir = Path(__file__).parent.parent / "evaluation"
    eval_dir.mkdir(exist_ok=True)
    eval_file = eval_dir / "eval_results.json"

    with open(eval_file, "w", encoding="utf-8") as f:
        json.dump({
            "model_path": model_path,
            "avg_score": avg_score,
            "results": results,
        }, f, ensure_ascii=False, indent=2)

    print(f"评估结果已保存到: {eval_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="模型评估")
    parser.add_argument("--model-path", type=str, default=str(Path(__file__).parent.parent / "merged"),
                        help="模型路径")
    args = parser.parse_args()

    evaluate_model(args.model_path)
