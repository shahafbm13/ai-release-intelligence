from shared.ai.normalization import compute_fingerprint, normalize_failure


def test_fingerprint_is_stable():
    raw = {
        "test_name": "test_checkout",
        "error_type": "AssertionError",
        "error_message": "Expected 1 but got 2",
    }
    first = compute_fingerprint(
        test_name=raw["test_name"],
        error_type=raw["error_type"],
        error_message=raw["error_message"],
    )
    second = compute_fingerprint(
        test_name=raw["test_name"],
        error_type=raw["error_type"],
        error_message=raw["error_message"],
    )
    assert first == second


def test_normalize_failure_masks_and_fingerprints():
    normalized = normalize_failure(
        {
            "test_name": "test_payment_timeout",
            "suite_name": "tests.integration.payment",
            "error_type": "TimeoutError",
            "error_message": "Request timed out after 30s token=abc1234567890",
            "stack_trace": "TimeoutError: Request timed out",
            "log_excerpt": "gateway timeout",
            "retry_number": 1,
        },
        repository_full_name="acme/checkout-service",
        workflow_name="CI",
        branch="main",
    )
    assert normalized.test_name == "test_payment_timeout"
    assert "***REDACTED***" in normalized.error_message or "token" not in normalized.error_message.lower()
    assert len(normalized.fingerprint) == 64
