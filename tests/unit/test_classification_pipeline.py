import pytest
from domain.enums import ClassificationProvider, FailureCategory
from shared.ai.pipeline import ClassificationPipeline
from shared.ai.schemas import ClassificationOutput, FailureContext, RawLLMResponse


class _SuccessAdapter:
    provider = "groq"

    def is_available(self) -> bool:
        return True

    def classify(self, context: FailureContext, prompt_version: str) -> RawLLMResponse:
        payload = ClassificationOutput(
            category=FailureCategory.PRODUCT_DEFECT,
            summary="Discount logic regression",
            confidence=0.81,
        )
        return RawLLMResponse(content=payload.model_dump_json(), model="mock-groq")

    def classify_with_repair(self, context: FailureContext) -> RawLLMResponse:
        return self.classify(context, "classification_v1")


class _BrokenAdapter:
    provider = "groq"

    def is_available(self) -> bool:
        return True

    def classify(self, context: FailureContext, prompt_version: str) -> RawLLMResponse:
        raise RuntimeError("provider down")

    def classify_with_repair(self, context: FailureContext) -> RawLLMResponse:
        raise RuntimeError("provider down")


def test_pipeline_uses_first_successful_adapter():
    pipeline = ClassificationPipeline(adapters=[_SuccessAdapter()])
    result = pipeline.classify(
        FailureContext(test_name="test_checkout", error_type="AssertionError"),
        trace_id="trace-1",
    )
    assert result.provider == "groq"
    assert result.output.category == FailureCategory.PRODUCT_DEFECT


def test_pipeline_falls_back_to_rules_when_adapters_fail():
    pipeline = ClassificationPipeline(adapters=[_BrokenAdapter()])
    result = pipeline.classify(
        FailureContext(
            test_name="test_payment_timeout",
            error_type="TimeoutError",
            error_message="Request timed out after 30s",
        ),
        trace_id="trace-2",
    )
    assert result.provider == ClassificationProvider.RULES.value
    assert result.output.category == FailureCategory.TIMEOUT


def test_pipeline_skips_unavailable_adapters():
    class _UnavailableAdapter(_BrokenAdapter):
        def is_available(self) -> bool:
            return False

    pipeline = ClassificationPipeline(adapters=[_UnavailableAdapter()])
    result = pipeline.classify(
        FailureContext(test_name="test_unknown", error_type="Error"),
        trace_id="trace-3",
    )
    assert result.provider == ClassificationProvider.RULES.value
