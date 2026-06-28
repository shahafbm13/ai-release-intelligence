from dataclasses import dataclass, field

RISK_ENGINE_VERSION = "v1"

CRITICAL_TEST_KEYWORDS = ("critical", "smoke", "p0", "blocker")


@dataclass(frozen=True)
class RiskFactor:
    name: str
    weight: float
    score: float
    contribution: float
    detail: str


@dataclass(frozen=True)
class FailureRiskInput:
    test_name: str
    category: str
    confidence: float
    retry_number: int
    has_stack_trace: bool
    has_log_excerpt: bool
    has_similar_match: bool
    similar_match_same_category: bool

    @property
    def is_critical(self) -> bool:
        lowered = self.test_name.lower()
        return any(keyword in lowered for keyword in CRITICAL_TEST_KEYWORDS)


@dataclass(frozen=True)
class ReleaseRiskInput:
    failures: list[FailureRiskInput] = field(default_factory=list)


@dataclass(frozen=True)
class ReleaseRiskResult:
    risk_level: str
    score: float
    factors: list[RiskFactor]
    missing_info: list[str]
    recommendation: str
    explanation: str
    engine_version: str = RISK_ENGINE_VERSION


def compute_release_risk(data: ReleaseRiskInput) -> ReleaseRiskResult:
    failures = data.failures
    missing_info: list[str] = []

    if not failures:
        return ReleaseRiskResult(
            risk_level="low",
            score=0.0,
            factors=[],
            missing_info=["no_failures_recorded"],
            recommendation="proceed",
            explanation="No failures were recorded for this CI run.",
        )

    failure_count = len(failures)
    failed_test_score = min(failure_count * 5.0, 20.0)

    critical_count = sum(1 for item in failures if item.is_critical)
    critical_score = min(critical_count * 10.0, 25.0)

    if any(not item.has_similar_match for item in failures):
        known_score = 20.0
        known_detail = "At least one failure has no historical similar match."
    elif all(item.similar_match_same_category for item in failures if item.has_similar_match):
        known_score = 5.0
        known_detail = "All matched failures share the same category as historical matches."
    else:
        known_score = 12.0
        known_detail = "Historical matches exist but categories differ."

    avg_confidence = sum(item.confidence for item in failures) / failure_count
    confidence_score = (1.0 - avg_confidence) * 15.0

    flaky_score = 0.0
    if any(item.retry_number > 0 or item.category == "flaky_intermittent" for item in failures):
        flaky_score = 10.0

    completeness_score = 10.0
    for item in failures:
        if not item.has_stack_trace:
            completeness_score -= 2.0
            missing_info.append(f"missing_stack_trace:{item.test_name}")
        if not item.has_log_excerpt:
            completeness_score -= 1.0
            missing_info.append(f"missing_log_excerpt:{item.test_name}")
    completeness_score = max(completeness_score, 0.0)

    factors = [
        RiskFactor(
            name="failed_test_count",
            weight=20.0,
            score=failed_test_score,
            contribution=failed_test_score,
            detail=f"{failure_count} failure(s); capped at 20 points.",
        ),
        RiskFactor(
            name="critical_test_failures",
            weight=25.0,
            score=critical_score,
            contribution=critical_score,
            detail=f"{critical_count} critical/smoke/p0 test(s); capped at 25 points.",
        ),
        RiskFactor(
            name="new_vs_known_failures",
            weight=20.0,
            score=known_score,
            contribution=known_score,
            detail=known_detail,
        ),
        RiskFactor(
            name="classification_confidence",
            weight=15.0,
            score=confidence_score,
            contribution=confidence_score,
            detail=f"Average classification confidence {avg_confidence:.2f}.",
        ),
        RiskFactor(
            name="flaky_indication",
            weight=10.0,
            score=flaky_score,
            contribution=flaky_score,
            detail="Retry or flaky category detected." if flaky_score else "No flaky indicators.",
        ),
        RiskFactor(
            name="data_completeness",
            weight=10.0,
            score=completeness_score,
            contribution=completeness_score,
            detail="Penalty applied for missing stack traces or log excerpts.",
        ),
    ]

    total_score = round(sum(factor.contribution for factor in factors), 2)
    risk_level = _score_to_level(total_score)
    recommendation = _level_to_recommendation(risk_level)
    explanation = (
        f"Release risk score {total_score}/100 ({risk_level}). "
        f"{failure_count} failing test(s) with advisory recommendation: {recommendation}."
    )

    return ReleaseRiskResult(
        risk_level=risk_level,
        score=total_score,
        factors=factors,
        missing_info=sorted(set(missing_info)),
        recommendation=recommendation,
        explanation=explanation,
    )


def _score_to_level(score: float) -> str:
    if score <= 25:
        return "low"
    if score <= 50:
        return "medium"
    if score <= 75:
        return "high"
    return "critical"


def _level_to_recommendation(level: str) -> str:
    if level == "low":
        return "proceed"
    if level == "medium":
        return "caution"
    return "hold"
