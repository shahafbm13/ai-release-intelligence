from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.deps import AuthenticatedUser
from api.schemas import ReleaseAssessmentResponse, RiskFactorResponse
from shared.repositories.ci_runs import CIRunRepository
from shared.repositories import RepositoryRepository
from shared.repositories.intelligence import ReleaseAssessmentRepository


class AssessmentService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._runs = CIRunRepository(session)
        self._assessments = ReleaseAssessmentRepository(session)
        self._repos = RepositoryRepository(session)

    def get_assessment(
        self,
        current_user: AuthenticatedUser,
        ci_run_id: UUID,
    ) -> ReleaseAssessmentResponse:
        run = self._runs.get_by_id(ci_run_id)
        if run is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": "CI run not found"},
            )
        repo = self._repos.get_by_id(run.repository_id)
        if repo is None or repo.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": "CI run not found"},
            )

        assessment = self._assessments.get_by_ci_run_id(ci_run_id)
        if assessment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": "Release assessment not found"},
            )

        factors = assessment.factors_json if isinstance(assessment.factors_json, list) else []
        missing_info = (
            assessment.missing_info_json if isinstance(assessment.missing_info_json, list) else []
        )
        return ReleaseAssessmentResponse(
            ci_run_id=ci_run_id,
            risk_level=assessment.risk_level,
            score=float(assessment.score),
            factors=[
                RiskFactorResponse(
                    name=item["name"],
                    weight=float(item["weight"]),
                    score=float(item["score"]),
                    contribution=float(item["contribution"]),
                    detail=item["detail"],
                )
                for item in factors
            ],
            missing_info=[str(item) for item in missing_info],
            recommendation=assessment.recommendation,
            explanation=assessment.explanation,
            engine_version=assessment.engine_version,
            created_at=assessment.created_at,
        )
