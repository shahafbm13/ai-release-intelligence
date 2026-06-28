from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
from uuid import UUID

from domain.enums import SimilarMatchMethod

SIMILARITY_WINDOW_DAYS = 90
MAX_SIMILAR_RESULTS = 20
MIN_MATCH_SCORE = 0.5


@dataclass(frozen=True)
class SimilarFailureMatch:
    matched_failure_id: UUID
    method: str
    score: float


@dataclass(frozen=True)
class HistoricalFailure:
    id: UUID
    ci_run_id: UUID
    test_name: str
    error_type: str
    error_message: str
    fingerprint: str
    created_at: datetime
    category: str | None = None


def message_similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, left.lower(), right.lower()).ratio()


def score_similarity(
    current: HistoricalFailure,
    candidate: HistoricalFailure,
) -> SimilarFailureMatch | None:
    if current.id == candidate.id or current.ci_run_id == candidate.ci_run_id:
        return None

    if current.fingerprint == candidate.fingerprint:
        return SimilarFailureMatch(
            matched_failure_id=candidate.id,
            method=SimilarMatchMethod.FINGERPRINT.value,
            score=1.0,
        )

    if (
        current.test_name == candidate.test_name
        and current.error_type
        and current.error_type == candidate.error_type
    ):
        return SimilarFailureMatch(
            matched_failure_id=candidate.id,
            method=SimilarMatchMethod.TEST_NAME_ERROR_TYPE.value,
            score=0.92,
        )

    if current.test_name == candidate.test_name:
        return SimilarFailureMatch(
            matched_failure_id=candidate.id,
            method=SimilarMatchMethod.TEST_NAME.value,
            score=0.8,
        )

    similarity = message_similarity(current.error_message, candidate.error_message)
    if current.error_type and current.error_type == candidate.error_type and similarity >= 0.85:
        return SimilarFailureMatch(
            matched_failure_id=candidate.id,
            method=SimilarMatchMethod.ERROR_MESSAGE.value,
            score=round(similarity * 0.9, 3),
        )

    if current.error_type and current.error_type == candidate.error_type:
        return SimilarFailureMatch(
            matched_failure_id=candidate.id,
            method=SimilarMatchMethod.ERROR_TYPE.value,
            score=0.6,
        )

    return None


def find_similar_failures(
    current: HistoricalFailure,
    candidates: list[HistoricalFailure],
    *,
    limit: int = MAX_SIMILAR_RESULTS,
) -> list[SimilarFailureMatch]:
    best_by_id: dict[UUID, SimilarFailureMatch] = {}
    for candidate in candidates:
        match = score_similarity(current, candidate)
        if match is None or match.score < MIN_MATCH_SCORE:
            continue
        existing = best_by_id.get(match.matched_failure_id)
        if existing is None or match.score > existing.score:
            best_by_id[match.matched_failure_id] = match

    ranked = sorted(best_by_id.values(), key=lambda item: item.score, reverse=True)
    return ranked[:limit]
