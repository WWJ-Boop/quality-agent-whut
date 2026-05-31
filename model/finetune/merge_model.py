"""合并LoRA权重脚本

将训练好的LoRA权重与基座模型合并，导出完整模型。
"""

import sys
from pathlib import Path

# 将项目根目录加入路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def merge_lora():
    """合并LoRA权重到基座模型"""
    try:
        from llamafactory.train.tuner import export_model
    except ImportError:
        print("请先安装LLaMA-Factory: pip install llama-factory")
        return

    lora_path = str(Path(__file__).parent.parent / "finetuned")
    output_path = str(Path(__file__).parent.parent / "merged")

    args = {
        "model_name_or_path": "Qwen/Qwen2.5-7B-Instruct",
        "trust_remote_code": True,
        "finetuning_type": "lora",
        "adapter_name_or_path": lora_path,
        "template": "qwen",
        "export_dir": output_path,
        "export_size": 2,
        "export_legacy_format": False,
    }

    print(f"LoRA权重路径: {lora_path}")
    print(f"输出路径: {output_path}")
    print("开始合并模型...")

    export_model(args)
    print(f"模型合并完成! 已保存到: {output_path}")


def merge_lora_simple():
    """使用PEFT库直接合并"""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    base_model_path = "Qwen/Qwen2.5-7B-Instruct"
    lora_path = str(Path(__file__).parent.parent / "finetuned")
    output_path = str(Path(__file__).parent.parent / "merged")

    print(f"加载基座模型: {base_model_path}")
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        torch_dtype=torch.bfloat16,
        device_map="cpu",
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(base_model_path, trust_remote_code=True)

    print(f"加载LoRA权重: {lora_path}")
    model = PeftModel.from_pretrained(base_model, lora_path)

    print("合并权重...")
    model = model.merge_and_unload()

    print(f"保存合并后的模型: {output_path}")
    model.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)

    print("模型合并完成!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="合并LoRA权重")
    parser.add_argument("--simple", action="store_true", help="使用简单合并方式")
    args = parser.parse_args()

    if args.simple:
        merge_lora_simple()
    else:
        merge_lora()
