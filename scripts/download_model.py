"""下载模型脚本

下载Qwen2.5-7B-Instruct基座模型和Embedding模型。
"""

import sys
from pathlib import Path

# 将项目根目录加入路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def download_base_model():
    """下载Qwen2.5-7B-Instruct基座模型"""
    from huggingface_hub import snapshot_download

    model_name = "Qwen/Qwen2.5-7B-Instruct"
    print(f"下载基座模型: {model_name}")

    try:
        snapshot_download(
            repo_id=model_name,
            local_dir=str(Path(__file__).parent.parent / "model" / "base" / "Qwen2.5-7B-Instruct"),
            resume_download=True,
        )
        print("基座模型下载完成!")
    except Exception as e:
        print(f"下载失败: {e}")
        print("请检查网络连接或设置HF_ENDPOINT环境变量")


def download_embedding_model():
    """下载Embedding模型"""
    from sentence_transformers import SentenceTransformer

    model_name = "shibing624/text2vec-large-chinese"
    print(f"下载Embedding模型: {model_name}")

    try:
        model = SentenceTransformer(model_name)
        # 保存到本地
        local_path = str(Path(__file__).parent.parent / "model" / "embedding" / "text2vec-large-chinese")
        model.save(local_path)
        print(f"Embedding模型已保存到: {local_path}")
    except Exception as e:
        print(f"下载失败: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="下载模型")
    parser.add_argument("--base", action="store_true", help="下载基座模型")
    parser.add_argument("--embedding", action="store_true", help="下载Embedding模型")
    parser.add_argument("--all", action="store_true", help="下载所有模型")
    args = parser.parse_args()

    if args.all or args.base:
        download_base_model()
    if args.all or args.embedding:
        download_embedding_model()
    if not any([args.base, args.embedding, args.all]):
        print("请指定要下载的模型: --base, --embedding, 或 --all")
