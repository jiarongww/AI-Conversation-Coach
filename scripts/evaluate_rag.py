from __future__ import annotations

import argparse
from pathlib import Path

from app.evaluation.ragas_eval import RAGEvaluator
from app.rag.qa_service import RAGQAService
from app.utils.io import read_jsonl
from app.utils.logging import setup_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate RAG system with ragas.")
    parser.add_argument("--eval-file", required=True, help="Path to JSONL evaluation set.")
    parser.add_argument("--persist-dir", required=True, help="Persist directory of vector index.")
    parser.add_argument("--mode", choices=["company_faq", "dating_reply"], default="company_faq")
    parser.add_argument("--output", default="./data/eval/rag_eval_result.csv", help="Output CSV file.")
    args = parser.parse_args()

    setup_logging()
    eval_samples = read_jsonl(args.eval_file)
    rag_service = RAGQAService(persist_dir=args.persist_dir, mode=args.mode)
    evaluator = RAGEvaluator(rag_service)
    df = evaluator.run(eval_samples)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(df)
    print(f"\nSaved evaluation result to: {output_path}")


if __name__ == "__main__":
    main()
