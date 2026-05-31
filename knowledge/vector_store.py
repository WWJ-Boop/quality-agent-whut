"""向量数据库模块

基于 Milvus 的向量存储与检索。
支持 Milvus Lite（本地嵌入式）和 Milvus Server 两种模式。
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from loguru import logger

from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility,
)

from knowledge.embedding import EmbeddingModel
from knowledge.text_splitter import TextChunk


@dataclass
class SearchResult:
    """检索结果"""
    content: str
    score: float
    metadata: dict


class VectorStore:
    """Milvus 向量数据库"""

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        collection_name: str = "quality_standards",
        host: str = "localhost",
        port: int = 19530,
        use_lite: bool = True,
    ):
        self.embedding_model = embedding_model
        self.collection_name = collection_name
        self.host = host
        self.port = port
        self.use_lite = use_lite
        self._collection = None

    def connect(self):
        """连接 Milvus"""
        if self.use_lite:
            connections.connect(alias="default", uri="milvus_lite.db")
            logger.info("已连接 Milvus Lite")
        else:
            connections.connect(alias="default", host=self.host, port=self.port)
            logger.info(f"已连接 Milvus Server: {self.host}:{self.port}")

    def create_collection(self, force: bool = False):
        """创建集合（如果不存在）"""
        if utility.has_collection(self.collection_name) and not force:
            logger.info(f"集合已存在: {self.collection_name}")
            self._collection = Collection(self.collection_name)
            return

        if force and utility.has_collection(self.collection_name):
            utility.drop_collection(self.collection_name)
            logger.info(f"已删除旧集合: {self.collection_name}")

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="filename", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_model.dimension),
        ]

        schema = CollectionSchema(fields=fields, description="工程质量标准知识库")
        self._collection = Collection(name=self.collection_name, schema=schema)

        # 创建向量索引
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128},
        }
        self._collection.create_index(field_name="embedding", index_params=index_params)
        logger.info(f"已创建集合: {self.collection_name}")

    @property
    def collection(self) -> Collection:
        if self._collection is None:
            self._collection = Collection(self.collection_name)
        return self._collection

    def add_chunks(self, chunks: List[TextChunk], batch_size: int = 100):
        """将文本块添加到向量数据库"""
        if not chunks:
            logger.warning("没有要添加的文本块")
            return

        total = len(chunks)
        for i in range(0, total, batch_size):
            batch = chunks[i:i + batch_size]
            contents = [c.content for c in batch]
            sources = [c.metadata.get("source", "") for c in batch]
            filenames = [c.metadata.get("filename", "") for c in batch]
            embeddings = self.embedding_model.embed_documents(contents)

            self.collection.insert([
                contents,
                sources,
                filenames,
                embeddings,
            ])
            logger.info(f"已插入 {min(i + batch_size, total)}/{total} 条记录")

        self.collection.flush()
        logger.info(f"共插入 {total} 条记录到 {self.collection_name}")

    def search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.0,
    ) -> List[SearchResult]:
        """语义检索"""
        query_embedding = self.embedding_model.embed_query(query)

        self.collection.load()

        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param={"metric_type": "COSINE", "params": {"nprobe": 16}},
            limit=top_k,
            output_fields=["content", "source", "filename"],
        )

        search_results = []
        for hits in results:
            for hit in hits:
                score = hit.score
                if score >= score_threshold:
                    search_results.append(SearchResult(
                        content=hit.entity.get("content"),
                        score=score,
                        metadata={
                            "source": hit.entity.get("source"),
                            "filename": hit.entity.get("filename"),
                        }
                    ))

        return search_results

    def delete_collection(self):
        """删除集合"""
        if utility.has_collection(self.collection_name):
            utility.drop_collection(self.collection_name)
            logger.info(f"已删除集合: {self.collection_name}")

    def get_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        self.collection.load()
        return {
            "collection_name": self.collection_name,
            "num_entities": self.collection.num_entities,
            "dimension": self.embedding_model.dimension,
        }
