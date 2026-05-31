"""文档加载与解析模块

支持PDF、Word、TXT等格式的工程质量标准文档加载。
"""

import os
from pathlib import Path
from typing import List, Optional

from PyPDF2 import PdfReader
from docx import Document
from loguru import logger


class DocumentLoader:
    """工程标准文档加载器"""

    def __init__(self):
        self.supported_extensions = {".pdf", ".docx", ".doc", ".txt", ".md"}

    def load(self, file_path: str) -> str:
        """加载单个文档，返回纯文本内容"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        ext = path.suffix.lower()
        if ext not in self.supported_extensions:
            raise ValueError(f"不支持的文件格式: {ext}")

        if ext == ".pdf":
            return self._load_pdf(path)
        elif ext in (".docx", ".doc"):
            return self._load_docx(path)
        elif ext in (".txt", ".md"):
            return self._load_text(path)

    def load_directory(self, dir_path: str) -> List[dict]:
        """加载目录下所有文档，返回文档列表 [{path, content, metadata}]"""
        path = Path(dir_path)
        if not path.is_dir():
            raise NotADirectoryError(f"目录不存在: {dir_path}")

        documents = []
        for file_path in sorted(path.rglob("*")):
            if file_path.suffix.lower() in self.supported_extensions:
                try:
                    content = self.load(str(file_path))
                    if content.strip():
                        documents.append({
                            "path": str(file_path),
                            "content": content,
                            "metadata": {
                                "source": str(file_path),
                                "filename": file_path.name,
                                "file_type": file_path.suffix,
                            }
                        })
                        logger.info(f"已加载文档: {file_path.name}")
                except Exception as e:
                    logger.warning(f"加载文档失败 {file_path.name}: {e}")

        logger.info(f"共加载 {len(documents)} 个文档")
        return documents

    def _load_pdf(self, path: Path) -> str:
        """解析PDF文档"""
        reader = PdfReader(str(path))
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text.strip())
        return "\n\n".join(text_parts)

    def _load_docx(self, path: Path) -> str:
        """解析Word文档"""
        doc = Document(str(path))
        paragraphs = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                paragraphs.append(text)
        return "\n\n".join(paragraphs)

    def _load_text(self, path: Path) -> str:
        """解析纯文本文件"""
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
