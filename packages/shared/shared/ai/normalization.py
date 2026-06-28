import hashlib
import re
from dataclasses import dataclass

from shared.ai.schemas import FailureContext
from shared.ai.secret_masker import mask_secrets


@dataclass(frozen=True)
class NormalizedFailure:
    test_name: str
    suite_name: str
    error_type: str
    error_message: str
    stack_trace: str
    log_excerpt: str
    retry_number: int
    fingerprint: str
    context: FailureContext


def _normalize_text(value: str, *, max_length: int = 4000) -> str:
    cleaned = " ".join(value.strip().split())
    cleaned = re.sub(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", "<uuid>", cleaned, flags=re.I)
    cleaned = re.sub(r"\b0x[0-9a-f]+\b", "<hex>", cleaned, flags=re.I)
    if len(cleaned) > max_length:
        return cleaned[: max_length - 3] + "..."
    return cleaned


def compute_fingerprint(
    *,
    test_name: str,
    error_type: str,
    error_message: str,
) -> str:
    normalized = "|".join(
        [
            test_name.strip().lower(),
            error_type.strip().lower(),
            _normalize_text(error_message, max_length=500).lower(),
        ]
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def normalize_failure(
    raw: dict,
    *,
    repository_full_name: str = "",
    workflow_name: str = "",
    branch: str = "",
) -> NormalizedFailure:
    test_name = _normalize_text(str(raw.get("test_name", "")), max_length=512)
    suite_name = _normalize_text(str(raw.get("suite_name", "")), max_length=512)
    error_type = _normalize_text(str(raw.get("error_type", "")), max_length=255)
    error_message = mask_secrets(_normalize_text(str(raw.get("error_message", ""))))
    stack_trace = mask_secrets(_normalize_text(str(raw.get("stack_trace", ""))))
    log_excerpt = mask_secrets(_normalize_text(str(raw.get("log_excerpt", ""))))
    retry_number = int(raw.get("retry_number", 0) or 0)

    context = FailureContext(
        test_name=test_name,
        suite_name=suite_name,
        error_type=error_type,
        error_message=error_message,
        stack_trace=stack_trace,
        log_excerpt=log_excerpt,
        retry_number=retry_number,
        repository_full_name=repository_full_name,
        workflow_name=workflow_name,
        branch=branch,
    )
    fingerprint = compute_fingerprint(
        test_name=test_name,
        error_type=error_type,
        error_message=error_message,
    )
    return NormalizedFailure(
        test_name=test_name,
        suite_name=suite_name,
        error_type=error_type,
        error_message=error_message,
        stack_trace=stack_trace,
        log_excerpt=log_excerpt,
        retry_number=retry_number,
        fingerprint=fingerprint,
        context=context,
    )
