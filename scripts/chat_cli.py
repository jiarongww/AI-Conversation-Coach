from __future__ import annotations

import argparse

from app.llm.client import LLMClient
from app.rag.qa_service import RAGQAService
from app.utils.logging import setup_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI for LLM or RAG chat.")
    parser.add_argument("--mode", choices=["company_faq", "dating_reply"], default="company_faq")
    parser.add_argument("--use-rag", action="store_true", help="Use RAG instead of plain LLM.")
    parser.add_argument("--persist-dir", default=None, help="Persist directory of vector index.")
    args = parser.parse_args()

    setup_logging()
    print(f"Mode: {args.mode} | use_rag={args.use_rag}")
    print("输入 quit 退出。\n")

    llm = LLMClient()
    rag_service = RAGQAService(persist_dir=args.persist_dir, mode=args.mode) if args.use_rag else None

    while True:
        user_input = input("你: ").strip()
        if user_input.lower() in {"quit", "exit", "q"}:
            print("Bye")
            break
        if not user_input:
            continue

        if rag_service:
            result = rag_service.ask(user_input)
            print(f"\n助手: {result.answer}\n")
        else:
            answer = llm.chat(user_input, mode=args.mode)
            print(f"\n助手: {answer}\n")


if __name__ == "__main__":
    main()
