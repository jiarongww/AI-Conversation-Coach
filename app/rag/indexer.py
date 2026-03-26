from __future__ import annotations

import logging
from pathlib import Path

from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.embeddings.dashscope import DashScopeEmbedding

from app.config import ensure_dir, get_settings

logger = logging.getLogger(__name__)


class RAGIndexer:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.embed_model = DashScopeEmbedding(model_name=self.settings.embed_model)

    def create_index(self, docs_dir: str | Path) -> VectorStoreIndex:
        logger.info("Loading documents from %s", docs_dir)
        documents = SimpleDirectoryReader(str(docs_dir)).load_data()
        logger.info("Loaded %s documents", len(documents))
        return VectorStoreIndex.from_documents(documents, embed_model=self.embed_model)

    def persist_index(self, docs_dir: str | Path, persist_dir: str | Path) -> None:
        persist_dir = ensure_dir(persist_dir)
        index = self.create_index(docs_dir)
        index.storage_context.persist(str(persist_dir))
        logger.info("Index persisted to %s", persist_dir)

    def load_index(self, persist_dir: str | Path) -> VectorStoreIndex:
        storage_context = StorageContext.from_defaults(persist_dir=str(persist_dir))
        logger.info("Loading index from %s", persist_dir)
        return load_index_from_storage(storage_context, embed_model=self.embed_model)
