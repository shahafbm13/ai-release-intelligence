from domain.enums import FailureCategory
from shared.ai.schemas import ClassificationOutput, FailureContext


def classify_with_rules(context: FailureContext) -> ClassificationOutput:
    haystack = " ".join(
        [
            context.error_type,
            context.error_message,
            context.stack_trace,
            context.log_excerpt,
            context.test_name,
            context.suite_name,
        ]
    ).lower()

    if any(token in haystack for token in ("timeout", "timed out", "timeouterror")):
        return ClassificationOutput(
            category=FailureCategory.TIMEOUT,
            subcategory="request_timeout",
            suspected_component=_guess_component(context),
            summary="Failure indicates a timeout waiting for a dependency or response.",
            likely_cause="Downstream service slow, network latency, or timeout threshold too low.",
            suggested_action="Inspect gateway/service latency and retry behavior; verify timeout configuration.",
            confidence=0.72,
            evidence_refs=_evidence(context, "timeout"),
            insufficient_information=False,
        )

    if any(token in haystack for token in ("401", "403", "unauthorized", "forbidden", "authentication")):
        return ClassificationOutput(
            category=FailureCategory.AUTHENTICATION_ISSUE,
            subcategory="auth_failure",
            suspected_component="auth",
            summary="Failure appears related to authentication or authorization.",
            likely_cause="Expired credentials, invalid token, or missing permissions.",
            suggested_action="Verify test credentials, token refresh, and service account scopes.",
            confidence=0.7,
            evidence_refs=_evidence(context, "auth"),
            insufficient_information=False,
        )

    if any(token in haystack for token in ("connection refused", "econnrefused", "503", "502", "504")):
        return ClassificationOutput(
            category=FailureCategory.INFRASTRUCTURE_ISSUE,
            subcategory="service_unavailable",
            suspected_component=_guess_component(context),
            summary="Failure suggests infrastructure or upstream service availability problems.",
            likely_cause="Service outage, bad deployment, or network partition.",
            suggested_action="Check service health dashboards and recent deployments.",
            confidence=0.68,
            evidence_refs=_evidence(context, "infra"),
            insufficient_information=False,
        )

    if any(token in haystack for token in ("connection reset", "network", "dns", "socket")):
        return ClassificationOutput(
            category=FailureCategory.NETWORK_ISSUE,
            subcategory="connectivity",
            suspected_component="network",
            summary="Failure indicates a network connectivity problem.",
            likely_cause="Transient network issue or misconfigured endpoint.",
            suggested_action="Verify endpoint reachability and network policies.",
            confidence=0.65,
            evidence_refs=_evidence(context, "network"),
            insufficient_information=False,
        )

    if "assertionerror" in haystack:
        category = FailureCategory.PRODUCT_DEFECT
        subcategory = "assertion_mismatch"
        if any(token in haystack for token in ("selector", "locator", "element not found", "stale element")):
            category = FailureCategory.TEST_DEFECT
            subcategory = "ui_selector"
        return ClassificationOutput(
            category=category,
            subcategory=subcategory,
            suspected_component=_guess_component(context),
            summary="Assertion failure during test execution.",
            likely_cause="Actual behavior diverged from expected result.",
            suggested_action="Review recent code changes and test expectations for the failing scenario.",
            confidence=0.55 if category == FailureCategory.PRODUCT_DEFECT else 0.6,
            evidence_refs=_evidence(context, "assertion"),
            insufficient_information=category == FailureCategory.UNKNOWN,
        )

    return ClassificationOutput(
        category=FailureCategory.UNKNOWN,
        subcategory="unclassified",
        suspected_component=_guess_component(context),
        summary="Insufficient signal to classify this failure confidently.",
        likely_cause="Not enough structured error information was available.",
        suggested_action="Review raw logs and recent changes manually.",
        confidence=0.35,
        evidence_refs=_evidence(context, "unknown"),
        insufficient_information=True,
    )


def _guess_component(context: FailureContext) -> str:
    if context.suite_name:
        parts = context.suite_name.split(".")
        if len(parts) >= 2:
            return parts[1]
        return parts[0]
    if context.test_name.startswith("test_"):
        return context.test_name.removeprefix("test_").split("_")[0]
    return "unknown"


def _evidence(context: FailureContext, label: str) -> list[str]:
    refs = [f"rule:{label}"]
    if context.error_type:
        refs.append(f"error_type:{context.error_type}")
    if context.test_name:
        refs.append(f"test_name:{context.test_name}")
    return refs
