"""文本分块模块

将长文档切分为适合向量化的小段落。
"""

from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class TextChunk:
    """文本块"""
    content: str
    metadata: dict = field(default_factory=dict)
    index: int = 0


class TextSplitter:
    """递归字符文本分块器

    按照段落、句子、词的优先级进行分割，保持语义完整性。
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: Optional[List[str]] = None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", "。", "；", ".", ";", "，", " ", ""]

    def split_text(self, text: str, metadata: Optional[dict] = None) -> List[TextChunk]:
        """将文本切分为多个块"""
        if not text.strip():
            return []

        chunks = self._recursive_split(text, self.separators)
        result = []
        for i, chunk in enumerate(chunks):
            if chunk.strip():
                result.append(TextChunk(
                    content=chunk.strip(),
                    metadata=metadata or {},
                    index=i,
                ))
        return result

    def split_documents(self, documents: List[dict]) -> List[TextChunk]:
        """批量切分文档列表

        Args:
            documents: [{content, metadata}] 格式的文档列表
        """
        all_chunks = []
        for doc in documents:
            chunks = self.split_text(doc["content"], doc.get("metadata", {}))
            all_chunks.extend(chunks)
        return all_chunks

    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        """递归分割文本"""
        if len(text) <= self.chunk_size:
            return [text]

        # 选择当前层级的分隔符
        separator = separators[0] if separators else ""
        remaining_separators = separators[1:] if len(separators) > 1 else []

        # 如果没有分隔符可用，按字符数硬切
        if not separator:
            return self._hard_split(text)

        # 按分隔符切分
        parts = text.split(separator)
        chunks = []
        current_chunk = ""

        for part in parts:
            # 单个部分就超长，递归到下一层
            if len(part) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                sub_chunks = self._recursive_split(part, remaining_separators)
                chunks.extend(sub_chunks)
            # 合并后超长，保存当前块，开始新块
            elif len(current_chunk) + len(part) + len(separator) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = part
            else:
                if current_chunk:
                    current_chunk = current_chunk + separator + part
                else:
                    current_chunk = part

        if current_chunk:
            chunks.append(current_chunk)

        # 处理重叠
        if self.chunk_overlap > 0 and len(chunks) > 1:
            chunks = self._add_overlap(chunks)

        return chunks

    def _hard_split(self, text: str) -> List[str]:
        """按字符数硬切分"""
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunks.append(text[start:end])
            start = end - self.chunk_overlap if self.chunk_overlap else end
        return chunks

    def _add_overlap(self, chunks: List[str]) -> List[str]:
        """为相邻块添加重叠部分"""
        result = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_tail = chunks[i - 1][-self.chunk_overlap:]
            result.append(prev_tail + chunks[i])
        return result
