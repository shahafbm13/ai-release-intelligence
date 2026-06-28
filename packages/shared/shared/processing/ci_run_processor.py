from uuid import UUID

import hashlib

from sqlalchemy.orm import Session

from domain.enums import ProcessingStatus
from domain.risk_engine import FailureRiskInput, ReleaseRiskInput, compute_release_risk
from shared.ai.normalization import normalize_failure
from shared.ai.pipeline import ClassificationPipeline
from shared.logging import get_logger
from shared.models import IngestedEventModel
from shared.repositories import RepositoryRepository
from shared.repositories.ci_runs import CIRunRepository
from shared.repositories.failures import ClassificationRepository, FailureOccurrenceRepository
from shared.repositories.intelligence import ReleaseAssessmentRepository, SimilarFailureLinkRepository
from shared.similarity.matcher import HistoricalFailure, find_similar_failures

logger = get_logger(__name__)


class CIRunProcessor:
    def __init__(
        self,
        session: Session,
        pipeline: ClassificationPipeline | None = None,
    ) -> None:
        self._session = session
        self._runs = CIRunRepository(session)
        self._failures = FailureOccurrenceRepository(session)
        self._classifications = ClassificationRepository(session)
        self._similar_links = SimilarFailureLinkRepository(session)
        self._assessments = ReleaseAssessmentRepository(session)
        self._repos = RepositoryRepository(session)
        self._pipeline = pipeline or ClassificationPipeline()

    def process(self, ci_run_id: UUID, correlation_id: str) -> dict:
        model = self._runs.get_model_by_id(ci_run_id)
        if model is None:
            logger.error("process_ci_run_not_found", ci_run_id=str(ci_run_id), correlation_id=correlation_id)
            return {"status": "not_found"}

        if model.processing_status == ProcessingStatus.COMPLETED.value:
            return {"status": "already_completed"}

        self._runs.update_processing_status(ci_run_id, ProcessingStatus.PROCESSING)
        self._session.commit()

        try:
            payload = self._load_payload(model.ingested_event_id)
            repository = self._repos.get_by_id(model.repository_id)
            repo_name = repository.full_name if repository else ""
            raw_failures = payload.get("test_failures", [])
            if not isinstance(raw_failures, list):
                raw_failures = []

            historical_candidates = self._failures.list_historical_by_repository(
                model.repository_id,
                exclude_ci_run_id=ci_run_id,
            )

            risk_inputs: list[FailureRiskInput] = []
            classified = 0

            for raw in raw_failures:
                if not isinstance(raw, dict):
                    continue
                normalized = normalize_failure(
                    raw,
                    repository_full_name=repo_name,
                    workflow_name=model.workflow_name,
                    branch=model.branch,
                )
                failure = self._failures.create(
                    ci_run_id=ci_run_id,
                    test_name=normalized.test_name,
                    suite_name=normalized.suite_name,
                    error_type=normalized.error_type,
                    error_message=normalized.error_message,
                    stack_trace=normalized.stack_trace,
                    log_excerpt=normalized.log_excerpt,
                    retry_number=normalized.retry_number,
                    fingerprint=normalized.fingerprint,
                )
                trace_id = hashlib.sha256(f"{correlation_id}:{failure.id}".encode("utf-8")).hexdigest()
                result = self._pipeline.classify(normalized.context, trace_id)
                classification = self._classifications.create(
                    failure_occurrence_id=failure.id,
                    category=result.output.category.value,
                    subcategory=result.output.subcategory,
                    suspected_component=result.output.suspected_component,
                    summary=result.output.summary,
                    likely_cause=result.output.likely_cause,
                    suggested_action=result.output.suggested_action,
                    confidence=result.output.confidence,
                    evidence_refs=result.output.evidence_refs,
                    insufficient_information=result.output.insufficient_information,
                    provider=result.provider,
                    model=result.model,
                    prompt_version=result.prompt_version,
                    input_hash=result.input_hash,
                    input_tokens=result.input_tokens,
                    output_tokens=result.output_tokens,
                    duration_ms=result.duration_ms,
                    trace_id=result.trace_id,
                )
                classified += 1

                current = HistoricalFailure(
                    id=failure.id,
                    ci_run_id=ci_run_id,
                    test_name=failure.test_name,
                    error_type=failure.error_type,
                    error_message=failure.error_message,
                    fingerprint=failure.fingerprint,
                    created_at=failure.created_at,
                    category=classification.category,
                )
                matches = find_similar_failures(current, historical_candidates)
                self._similar_links.replace_for_failure(
                    failure_occurrence_id=failure.id,
                    links=[
                        (match.matched_failure_id, match.method, match.score) for match in matches
                    ],
                )

                matched_categories = [
                    candidate.category
                    for candidate in historical_candidates
                    if candidate.id in {match.matched_failure_id for match in matches}
                ]
                risk_inputs.append(
                    FailureRiskInput(
                        test_name=failure.test_name,
                        category=classification.category,
                        confidence=classification.confidence,
                        retry_number=failure.retry_number,
                        has_stack_trace=bool(failure.stack_trace.strip()),
                        has_log_excerpt=bool(failure.log_excerpt.strip()),
                        has_similar_match=bool(matches),
                        similar_match_same_category=any(
                            category == classification.category for category in matched_categories if category
                        ),
                    )
                )

            assessment = compute_release_risk(ReleaseRiskInput(failures=risk_inputs))
            self._assessments.upsert(ci_run_id=ci_run_id, result=assessment)

            model.failure_count = classified
            self._runs.update_processing_status(ci_run_id, ProcessingStatus.COMPLETED)
            self._session.commit()
            logger.info(
                "process_ci_run_completed",
                ci_run_id=str(ci_run_id),
                correlation_id=correlation_id,
                failure_count=classified,
                risk_level=assessment.risk_level,
                risk_score=assessment.score,
            )
            return {
                "status": "completed",
                "failure_count": classified,
                "classified": classified,
                "risk_level": assessment.risk_level,
                "risk_score": assessment.score,
            }
        except Exception as exc:
            self._session.rollback()
            self._runs.update_processing_status(ci_run_id, ProcessingStatus.FAILED)
            self._session.commit()
            logger.error(
                "process_ci_run_failed",
                ci_run_id=str(ci_run_id),
                correlation_id=correlation_id,
                error=str(exc),
            )
            raise

    def backfill_release_assessments(self, organization_id: UUID) -> int:
        from sqlalchemy import select

        from shared.models import CIRunModel, ReleaseAssessmentModel, RepositoryModel

        run_ids = self._session.scalars(
            select(CIRunModel.id)
            .join(RepositoryModel, CIRunModel.repository_id == RepositoryModel.id)
            .outerjoin(ReleaseAssessmentModel, ReleaseAssessmentModel.ci_run_id == CIRunModel.id)
            .where(
                RepositoryModel.organization_id == organization_id,
                CIRunModel.processing_status == ProcessingStatus.COMPLETED.value,
                ReleaseAssessmentModel.id.is_(None),
            )
        ).all()

        updated = 0
        for ci_run_id in run_ids:
            risk_inputs = self._build_risk_inputs_for_run(ci_run_id)
            assessment = compute_release_risk(ReleaseRiskInput(failures=risk_inputs))
            self._assessments.upsert(ci_run_id=ci_run_id, result=assessment)
            updated += 1
            logger.info(
                "backfill_release_assessment",
                ci_run_id=str(ci_run_id),
                risk_level=assessment.risk_level,
                risk_score=assessment.score,
            )
        return updated

    def _build_risk_inputs_for_run(self, ci_run_id: UUID) -> list[FailureRiskInput]:
        model = self._runs.get_model_by_id(ci_run_id)
        if model is None:
            return []

        historical_candidates = self._failures.list_historical_by_repository(
            model.repository_id,
            exclude_ci_run_id=ci_run_id,
        )
        candidate_categories = {candidate.id: candidate.category for candidate in historical_candidates}

        risk_inputs: list[FailureRiskInput] = []
        for failure in self._failures.list_by_ci_run(ci_run_id):
            classification = self._classifications.get_by_failure_id(failure.id)
            if classification is None:
                continue

            links = self._similar_links.list_for_failure(failure.id)
            if not links:
                current = HistoricalFailure(
                    id=failure.id,
                    ci_run_id=ci_run_id,
                    test_name=failure.test_name,
                    error_type=failure.error_type,
                    error_message=failure.error_message,
                    fingerprint=failure.fingerprint,
                    created_at=failure.created_at,
                    category=classification.category,
                )
                matches = find_similar_failures(current, historical_candidates)
                if matches:
                    self._similar_links.replace_for_failure(
                        failure_occurrence_id=failure.id,
                        links=[
                            (match.matched_failure_id, match.method, match.score)
                            for match in matches
                        ],
                    )
                    links = self._similar_links.list_for_failure(failure.id)

            matched_categories = [
                candidate_categories.get(link.matched_failure_occurrence_id)
                for link in links
            ]
            risk_inputs.append(
                FailureRiskInput(
                    test_name=failure.test_name,
                    category=classification.category,
                    confidence=classification.confidence,
                    retry_number=failure.retry_number,
                    has_stack_trace=bool(failure.stack_trace.strip()),
                    has_log_excerpt=bool(failure.log_excerpt.strip()),
                    has_similar_match=bool(links),
                    similar_match_same_category=any(
                        category == classification.category
                        for category in matched_categories
                        if category
                    ),
                )
            )
        return risk_inputs

    def _load_payload(self, ingested_event_id: UUID | None) -> dict:
        if ingested_event_id is None:
            return {}
        ingested = self._session.get(IngestedEventModel, ingested_event_id)
        if ingested is None or not isinstance(ingested.payload_json, dict):
            return {}
        return ingested.payload_json
