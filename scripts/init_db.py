"""初始化知识库脚本

加载标准文档，切分并向量化存入 Milvus。
用法:
    python scripts/init_db.py                    # 初始化默认知识库
    python scripts/init_db.py --add-doc file.pdf # 添加单个文档
    python scripts/init_db.py --rebuild          # 重建知识库
"""

import sys
import argparse
from pathlib import Path

# 将项目根目录加入路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from knowledge import DocumentLoader, TextSplitter, EmbeddingModel, VectorStore


def init_knowledge_base(standards_dir: str = "data/standards", rebuild: bool = False):
    """初始化知识库"""
    logger.info("开始初始化知识库...")

    # 1. 加载文档
    loader = DocumentLoader()
    documents = loader.load_directory(standards_dir)
    if not documents:
        logger.warning(f"目录 {standards_dir} 中没有找到文档")
        logger.info("请将工程质量标准文档(PDF/Word/TXT)放入 data/standards/ 目录")
        return

    # 2. 切分文档
    splitter = TextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    logger.info(f"文档切分完成，共 {len(chunks)} 个文本块")

    # 3. 初始化向量模型和数据库
    embedding_model = EmbeddingModel()
    vector_store = VectorStore(embedding_model=embedding_model)

    # 4. 连接并创建集合
    vector_store.connect()
    vector_store.create_collection(force=rebuild)

    # 5. 添加文本块
    vector_store.add_chunks(chunks)

    # 6. 显示统计
    stats = vector_store.get_stats()
    logger.info(f"知识库初始化完成: {stats}")


def add_document(file_path: str):
    """添加单个文档到知识库"""
    logger.info(f"添加文档: {file_path}")

    loader = DocumentLoader()
    content = loader.load(file_path)

    splitter = TextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(content, metadata={
        "source": file_path,
        "filename": Path(file_path).name,
    })

    embedding_model = EmbeddingModel()
    vector_store = VectorStore(embedding_model=embedding_model)
    vector_store.connect()
    vector_store.add_chunks(chunks)

    logger.info(f"文档添加完成，共 {len(chunks)} 个文本块")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="初始化工程质量标准知识库")
    parser.add_argument("--add-doc", type=str, help="添加单个文档路径")
    parser.add_argument("--rebuild", action="store_true", help="重建知识库")
    parser.add_argument("--standards-dir", type=str, default="data/standards", help="标准文档目录")
    args = parser.parse_args()

    if args.add_doc:
        add_document(args.add_doc)
    else:
        init_knowledge_base(args.standards_dir, args.rebuild)
