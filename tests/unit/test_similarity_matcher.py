from datetime import UTC, datetime
from uuid import uuid4

from domain.enums import SimilarMatchMethod
from shared.similarity.matcher import HistoricalFailure, find_similar_failures, score_similarity


def _failure(**kwargs) -> HistoricalFailure:
    defaults = {
        "id": uuid4(),
        "ci_run_id": uuid4(),
        "test_name": "test_checkout_applies_discount",
        "error_type": "AssertionError",
        "error_message": "Expected total 90.0 but got 100.0",
        "fingerprint": "abc123",
        "created_at": datetime.now(UTC),
        "category": "product_defect",
    }
    defaults.update(kwargs)
    return HistoricalFailure(**defaults)


def test_fingerprint_match_scores_highest():
    current = _failure()
    candidate = _failure(
        id=uuid4(),
        ci_run_id=uuid4(),
        fingerprint=current.fingerprint,
    )
    match = score_similarity(current, candidate)
    assert match is not None
    assert match.method == SimilarMatchMethod.FINGERPRINT.value
    assert match.score == 1.0


def test_find_similar_failures_is_deterministic():
    current = _failure()
    candidates = [
        _failure(
            test_name="test_other",
            error_type="TimeoutError",
            error_message="timeout",
            fingerprint="other",
        ),
        _failure(
            test_name=current.test_name,
            error_type=current.error_type,
            fingerprint="different",
        ),
    ]
    first = find_similar_failures(current, candidates)
    second = find_similar_failures(current, candidates)
    assert first == second
    assert first[0].method == SimilarMatchMethod.TEST_NAME_ERROR_TYPE.value
