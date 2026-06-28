import hashlib
import time
from pathlib import Path
from typing import Protocol

import httpx

from shared.ai.json_repair import parse_classification_output
from shared.ai.schemas import FailureContext, RawLLMResponse
from shared.config import Settings

PROMPT_VERSION = "classification_v1"
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "classification_v1.txt"
REPAIR_SUFFIX = (
    "\n\nYour previous response was invalid JSON. "
    "Return ONLY JSON that matches the schema exactly."
)


class LLMProviderAdapter(Protocol):
    provider: str

    def is_available(self) -> bool: ...

    def classify(self, context: FailureContext, prompt_version: str) -> RawLLMResponse: ...


def load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def build_user_prompt(context: FailureContext) -> str:
    return (
        "Classify this CI test failure:\n"
        f"repository: {context.repository_full_name}\n"
        f"workflow: {context.workflow_name}\n"
        f"branch: {context.branch}\n"
        f"test_name: {context.test_name}\n"
        f"suite_name: {context.suite_name}\n"
        f"error_type: {context.error_type}\n"
        f"error_message: {context.error_message}\n"
        f"stack_trace: {context.stack_trace}\n"
        f"log_excerpt: {context.log_excerpt}\n"
        f"retry_number: {context.retry_number}\n"
    )


def compute_input_hash(context: FailureContext) -> str:
    payload = context.model_dump_json()
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class GroqAdapter:
    provider = "groq"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def is_available(self) -> bool:
        return bool(self._settings.groq_api_key)

    def classify(self, context: FailureContext, prompt_version: str) -> RawLLMResponse:
        return self._call(context, repair=False)

    def classify_with_repair(self, context: FailureContext) -> RawLLMResponse:
        return self._call(context, repair=True)

    def _call(self, context: FailureContext, *, repair: bool) -> RawLLMResponse:
        system_prompt = load_system_prompt()
        user_prompt = build_user_prompt(context)
        if repair:
            user_prompt += REPAIR_SUFFIX

        started = time.perf_counter()
        response = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {self._settings.groq_api_key}"},
            json={
                "model": self._settings.groq_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
            },
            timeout=30.0,
        )
        response.raise_for_status()
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
        usage = payload.get("usage", {})
        duration_ms = int((time.perf_counter() - started) * 1000)
        parse_classification_output(content)
        return RawLLMResponse(
            content=content,
            model=self._settings.groq_model,
            input_tokens=int(usage.get("prompt_tokens", 0)),
            output_tokens=int(usage.get("completion_tokens", 0)),
            duration_ms=duration_ms,
        )


class GeminiAdapter:
    provider = "gemini"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def is_available(self) -> bool:
        return bool(self._settings.gemini_api_key)

    def classify(self, context: FailureContext, prompt_version: str) -> RawLLMResponse:
        return self._call(context, repair=False)

    def classify_with_repair(self, context: FailureContext) -> RawLLMResponse:
        return self._call(context, repair=True)

    def _call(self, context: FailureContext, *, repair: bool) -> RawLLMResponse:
        prompt = f"{load_system_prompt()}\n\n{build_user_prompt(context)}"
        if repair:
            prompt += REPAIR_SUFFIX

        started = time.perf_counter()
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._settings.gemini_model}:generateContent"
        )
        response = httpx.post(
            url,
            params={"key": self._settings.gemini_api_key},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.1,
                    "responseMimeType": "application/json",
                },
            },
            timeout=30.0,
        )
        response.raise_for_status()
        payload = response.json()
        content = payload["candidates"][0]["content"]["parts"][0]["text"]
        usage = payload.get("usageMetadata", {})
        duration_ms = int((time.perf_counter() - started) * 1000)
        parse_classification_output(content)
        return RawLLMResponse(
            content=content,
            model=self._settings.gemini_model,
            input_tokens=int(usage.get("promptTokenCount", 0)),
            output_tokens=int(usage.get("candidatesTokenCount", 0)),
            duration_ms=duration_ms,
        )
