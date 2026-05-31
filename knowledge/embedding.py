"""向量化模块

使用中文Embedding模型将文本转换为向量。
"""

from typing import List, Optional
from loguru import logger


class EmbeddingModel:
    """中文文本向量化模型

    基于 sentence-transformers 加载本地或远程 Embedding 模型。
    默认使用 shibing624/text2vec-large-chinese。
    """

    def __init__(
        self,
        model_name: str = "shibing624/text2vec-large-chinese",
        device: Optional[str] = None,
    ):
        self.model_name = model_name
        self.device = device
        self._model = None

    @property
    def model(self):
        """延迟加载模型"""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info(f"加载Embedding模型: {self.model_name}")
            self._model = SentenceTransformer(
                self.model_name,
                device=self.device,
            )
            logger.info(f"Embedding模型加载完成，维度: {self._model.get_sentence_embedding_dimension()}")
        return self._model

    @property
    def dimension(self) -> int:
        """向量维度"""
        return self.model.get_sentence_embedding_dimension()

    def embed_query(self, text: str) -> List[float]:
        """将单条文本转为向量，用于查询"""
        return self.model.encode(text, normalize_embeddings=True).tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量将文本转为向量，用于文档索引"""
        if not texts:
            return []
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
            batch_size=32,
        )
        return embeddings.tolist()

    def embed_batch(self, texts: List[str], batch_size: int = 64) -> List[List[float]]:
        """分批向量化，适合大量文档"""
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.embed_documents(batch)
            all_embeddings.extend(embeddings)
            logger.info(f"向量化进度: {min(i + batch_size, len(texts))}/{len(texts)}")
        return all_embeddings
