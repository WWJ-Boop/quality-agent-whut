"""RAG知识库模块"""

from knowledge.document_loader import DocumentLoader
from knowledge.text_splitter import TextSplitter, TextChunk


def __getattr__(name):
    """延迟导入重型依赖模块（sentence_transformers、pymilvus），
    仅在实际使用时才加载，避免在无 GPU 环境下崩溃。"""
    if name == "EmbeddingModel":
        from knowledge.embedding import EmbeddingModel
        return EmbeddingModel
    if name == "VectorStore":
        from knowledge.vector_store import VectorStore
        return VectorStore
    if name == "SearchResult":
        from knowledge.vector_store import SearchResult
        return SearchResult
    raise AttributeError(f"module 'knowledge' has no attribute {name!r}")


__all__ = [
    "DocumentLoader",
    "TextSplitter",
    "TextChunk",
    "EmbeddingModel",
    "VectorStore",
    "SearchResult",
]
