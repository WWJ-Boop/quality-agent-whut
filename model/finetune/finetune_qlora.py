"""QLoRA微调脚本

基于LLaMA-Factory对Qwen2.5-7B进行领域微调。
支持QLoRA（4-bit量化 + LoRA）训练。
"""

import sys
from pathlib import Path

# 将项目根目录加入路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def finetune():
    """执行QLoRA微调"""
    try:
        from llamafactory.train.tuner import run_exp
    except ImportError:
        print("请先安装LLaMA-Factory: pip install llama-factory")
        print("或: git clone https://github.com/hiyouga/LLaMA-Factory.git && cd LLaMA-Factory && pip install -e .")
        return

    # 训练配置
    args = {
        # 模型配置
        "model_name_or_path": "Qwen/Qwen2.5-7B-Instruct",
        "trust_remote_code": True,

        # 训练方法
        "stage": "sft",
        "do_train": True,
        "finetuning_type": "lora",

        # LoRA配置
        "lora_rank": 64,
        "lora_alpha": 128,
        "lora_dropout": 0.05,
        "lora_target": "all",

        # 量化配置（QLoRA）
        "quantization_bit": 4,
        "quantization_method": "bitsandbytes",

        # 数据配置
        "dataset_dir": str(Path(__file__).parent.parent.parent / "data" / "training"),
        "dataset": "train_formatted",
        "template": "qwen",
        "cutoff_len": 2048,
        "max_samples": 1000,
        "overwrite_cache": True,

        # 训练超参数
        "output_dir": str(Path(__file__).parent.parent / "finetuned"),
        "num_train_epochs": 3,
        "per_device_train_batch_size": 4,
        "gradient_accumulation_steps": 4,
        "learning_rate": 2e-4,
        "warmup_ratio": 0.1,
        "lr_scheduler_type": "cosine",
        "bf16": True,
        "logging_steps": 10,
        "save_strategy": "epoch",
        "eval_strategy": "epoch",
        "val_size": 0.1,

        # 其他
        "report_to": "none",
        "seed": 42,
    }

    print("开始QLoRA微调...")
    print(f"基座模型: {args['model_name_or_path']}")
    print(f"输出目录: {args['output_dir']}")
    print(f"训练轮数: {args['num_train_epochs']}")
    print(f"学习率: {args['learning_rate']}")

    run_exp(args)
    print("微调完成!")


def finetune_with_config(config_path: str):
    """使用YAML配置文件进行微调"""
    import yaml

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    try:
        from llamafactory.train.tuner import run_exp
        run_exp(config)
    except ImportError:
        print("请先安装LLaMA-Factory")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="QLoRA微调脚本")
    parser.add_argument("--config", type=str, help="配置文件路径")
    args = parser.parse_args()

    if args.config:
        finetune_with_config(args.config)
    else:
        finetune()
