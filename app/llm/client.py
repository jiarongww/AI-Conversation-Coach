from __future__ import annotations

from typing import Iterable

from openai import OpenAI

from app.config import get_settings
from app.llm.prompts import PromptMode, get_prompt_pack


class LLMClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        self.client = OpenAI(api_key=settings.api_key, base_url=settings.base_url)

    def chat(
        self,
        user_message: str,
        mode: PromptMode = "company_faq",
        temperature: float = 0.3,
    ) -> str:
        prompt_pack = get_prompt_pack(mode)
        completion = self.client.chat.completions.create(
            model=self.settings.chat_model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": prompt_pack.system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return completion.choices[0].message.content or ""

    def stream_chat(
        self,
        user_message: str,
        mode: PromptMode = "company_faq",
        temperature: float = 0.3,
    ) -> Iterable[str]:
        prompt_pack = get_prompt_pack(mode)
        completion = self.client.chat.completions.create(
            model=self.settings.chat_model,
            temperature=temperature,
            stream=True,
            messages=[
                {"role": "system", "content": prompt_pack.system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        for chunk in completion:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield delta
