from domain.risk_engine import FailureRiskInput, ReleaseRiskInput, compute_release_risk


def test_golden_high_risk_multiple_new_failures():
    result = compute_release_risk(
        ReleaseRiskInput(
            failures=[
                FailureRiskInput(
                    test_name="test_critical_checkout",
                    category="product_defect",
                    confidence=0.4,
                    retry_number=1,
                    has_stack_trace=False,
                    has_log_excerpt=False,
                    has_similar_match=False,
                    similar_match_same_category=False,
                ),
                FailureRiskInput(
                    test_name="test_payment_timeout",
                    category="timeout",
                    confidence=0.5,
                    retry_number=0,
                    has_stack_trace=True,
                    has_log_excerpt=True,
                    has_similar_match=False,
                    similar_match_same_category=False,
                ),
            ]
        )
    )
    assert result.risk_level in {"high", "critical"}
    assert result.score >= 51
    assert result.recommendation == "hold"
    assert any(factor.name == "failed_test_count" for factor in result.factors)


def test_golden_low_risk_known_failure():
    result = compute_release_risk(
        ReleaseRiskInput(
            failures=[
                FailureRiskInput(
                    test_name="test_minor_log",
                    category="test_defect",
                    confidence=0.9,
                    retry_number=0,
                    has_stack_trace=True,
                    has_log_excerpt=True,
                    has_similar_match=True,
                    similar_match_same_category=True,
                )
            ]
        )
    )
    assert result.risk_level == "low"
    assert result.score <= 25
    assert result.recommendation == "proceed"


def test_golden_medium_risk_caution():
    result = compute_release_risk(
        ReleaseRiskInput(
            failures=[
                FailureRiskInput(
                    test_name="test_checkout_applies_discount",
                    category="product_defect",
                    confidence=0.55,
                    retry_number=0,
                    has_stack_trace=True,
                    has_log_excerpt=True,
                    has_similar_match=True,
                    similar_match_same_category=False,
                ),
                FailureRiskInput(
                    test_name="test_api_health",
                    category="infrastructure_issue",
                    confidence=0.6,
                    retry_number=0,
                    has_stack_trace=True,
                    has_log_excerpt=False,
                    has_similar_match=False,
                    similar_match_same_category=False,
                ),
            ]
        )
    )
    assert result.risk_level in {"medium", "high"}
    assert result.recommendation in {"caution", "hold"}
    assert "missing_log_excerpt" in " ".join(result.missing_info)
