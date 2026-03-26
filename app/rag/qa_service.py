from __future__ import annotations

import logging
from pathlib import Path

from llama_index.core import PromptTemplate
from llama_index.llms.openai_like import OpenAILike

from app.config import get_settings
from app.llm.prompts import PromptMode, get_prompt_pack
from app.rag.indexer import RAGIndexer
from app.rag.schemas import QAResult

logger = logging.getLogger(__name__)


class RAGQAService:
    def __init__(self, persist_dir: str | Path | None = None, mode: PromptMode = "company_faq") -> None:
        self.settings = get_settings()
        self.mode = mode
        self.persist_dir = str(persist_dir or self.settings.rag_persist_dir)
        self.indexer = RAGIndexer()
        self.index = self.indexer.load_index(self.persist_dir)
        self.query_engine = self._build_query_engine()
        self.retriever = self.index.as_retriever(similarity_top_k=self.settings.top_k)

    def _build_query_engine(self):
        llm = OpenAILike(
            model=self.settings.chat_model,
            api_base=self.settings.base_url,
            api_key=self.settings.api_key,
            is_chat_model=True,
            temperature=0.2,
        )
        query_engine = self.index.as_query_engine(
            llm=llm,
            similarity_top_k=self.settings.top_k,
            streaming=False,
        )
        return self._apply_prompt(query_engine)

    def _apply_prompt(self, query_engine):
        prompt_pack = get_prompt_pack(self.mode)
        qa_prompt = PromptTemplate(prompt_pack.rag_template)
        query_engine.update_prompts({"response_synthesizer:text_qa_template": qa_prompt})
        return query_engine

    def retrieve(self, question: str) -> list[str]:
        logger.info("Retrieval query received: %s", question)
        nodes = self.retriever.retrieve(question)
        contexts: list[str] = []
        for node in nodes or []:
            try:
                contexts.append(node.get_content())
            except Exception:
                if hasattr(node, "node") and hasattr(node.node, "get_content"):
                    contexts.append(node.node.get_content())
        return contexts

    def ask(self, question: str) -> QAResult:
        logger.info("Query received: %s", question)
        response = self.query_engine.query(question)
        answer = getattr(response, "response", None) or getattr(response, "response_txt", "") or str(response)
        contexts = []
        for node in getattr(response, "source_nodes", []) or []:
            try:
                contexts.append(node.get_content())
            except Exception:
                if hasattr(node, "node") and hasattr(node.node, "get_content"):
                    contexts.append(node.node.get_content())
        return QAResult(question=question, answer=answer, contexts=contexts)
