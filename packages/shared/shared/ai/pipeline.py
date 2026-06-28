import time
from typing import Iterable

from domain.enums import ClassificationProvider
from shared.ai.adapters.llm import (
    PROMPT_VERSION,
    GeminiAdapter,
    GroqAdapter,
    compute_input_hash,
)
from shared.ai.json_repair import parse_classification_output
from shared.ai.rule_classifier import classify_with_rules
from shared.ai.schemas import ClassificationResult, FailureContext
from shared.config import Settings, get_settings
from shared.logging import get_logger

logger = get_logger(__name__)


class ClassificationPipeline:
    def __init__(
        self,
        settings: Settings | None = None,
        adapters: Iterable[object] | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._adapters = list(adapters) if adapters is not None else [
            GroqAdapter(self._settings),
            GeminiAdapter(self._settings),
        ]

    def classify(self, context: FailureContext, trace_id: str) -> ClassificationResult:
        input_hash = compute_input_hash(context)
        started = time.perf_counter()

        for adapter in self._adapters:
            if not adapter.is_available():
                logger.info(
                    "classification_adapter_skipped",
                    provider=adapter.provider,
                    trace_id=trace_id,
                    reason="not_configured",
                )
                continue
            try:
                raw = adapter.classify(context, PROMPT_VERSION)
                output = parse_classification_output(raw.content)
                return ClassificationResult(
                    output=output,
                    provider=adapter.provider,
                    model=raw.model,
                    prompt_version=PROMPT_VERSION,
                    input_hash=input_hash,
                    input_tokens=raw.input_tokens,
                    output_tokens=raw.output_tokens,
                    duration_ms=raw.duration_ms,
                    trace_id=trace_id,
                )
            except Exception as exc:
                logger.warning(
                    "classification_adapter_failed",
                    provider=adapter.provider,
                    trace_id=trace_id,
                    error=str(exc),
                )
                try:
                    raw = adapter.classify_with_repair(context)
                    output = parse_classification_output(raw.content, allow_repair=True)
                    return ClassificationResult(
                        output=output,
                        provider=adapter.provider,
                        model=raw.model,
                        prompt_version=PROMPT_VERSION,
                        input_hash=input_hash,
                        input_tokens=raw.input_tokens,
                        output_tokens=raw.output_tokens,
                        duration_ms=raw.duration_ms,
                        trace_id=trace_id,
                    )
                except Exception as repair_exc:
                    logger.warning(
                        "classification_adapter_repair_failed",
                        provider=adapter.provider,
                        trace_id=trace_id,
                        error=str(repair_exc),
                    )

        output = classify_with_rules(context)
        duration_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "classification_rule_fallback",
            trace_id=trace_id,
            category=output.category.value,
        )
        return ClassificationResult(
            output=output,
            provider=ClassificationProvider.RULES.value,
            model="rules_v1",
            prompt_version=PROMPT_VERSION,
            input_hash=input_hash,
            input_tokens=0,
            output_tokens=0,
            duration_ms=duration_ms,
            trace_id=trace_id,
        )
