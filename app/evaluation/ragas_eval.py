from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

import pandas as pd
from datasets import Dataset
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.llms.tongyi import Tongyi
from ragas import evaluate
from ragas.metrics import answer_correctness, context_precision, context_recall

from app.config import get_settings
from app.rag.qa_service import RAGQAService


class RAGEvaluator:
    def __init__(self, rag_service: RAGQAService) -> None:
        settings = get_settings()
        self.rag_service = rag_service
        self.llm = Tongyi(model_name=settings.chat_model)
        self.embeddings = DashScopeEmbeddings(model=settings.embed_model)

    def run(self, eval_samples: Iterable[dict]) -> pd.DataFrame:
        questions: list[str] = []
        answers: list[str] = []
        contexts: list[list[str]] = []
        ground_truths: list[str] = []

        for sample in eval_samples:
            question = sample["question"]
            ground_truth = sample["ground_truth"]
            result = self.rag_service.ask(question)
            questions.append(question)
            answers.append(result.answer)
            contexts.append(result.contexts)
            ground_truths.append(ground_truth)

        dataset = Dataset.from_dict(
            {
                "question": questions,
                "answer": answers,
                "contexts": contexts,
                "ground_truth": ground_truths,
            }
        )

        score = evaluate(
            dataset=dataset,
            metrics=[answer_correctness, context_recall, context_precision],
            llm=self.llm,
            embeddings=self.embeddings,
        )
        result_df = score.to_pandas()
        result_df.insert(0, "question", questions)
        result_df.insert(1, "answer", answers)
        result_df.insert(2, "ground_truth", ground_truths)
        return result_df
