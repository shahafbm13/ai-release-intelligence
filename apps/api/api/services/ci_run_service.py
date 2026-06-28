from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.deps import AuthenticatedUser
from api.schemas import CIRunResponse, PaginatedCIRunsResponse
from shared.repositories.ci_runs import CIRunRepository


class CIRunService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._runs = CIRunRepository(session)

    def list_runs(
        self,
        current_user: AuthenticatedUser,
        *,
        page: int = 1,
        page_size: int = 20,
        conclusion: str | None = None,
    ) -> PaginatedCIRunsResponse:
        offset = (page - 1) * page_size
        runs = self._runs.list_by_organization(
            current_user.organization_id,
            conclusion=conclusion,
            limit=page_size,
            offset=offset,
        )
        total = self._runs.count_by_organization(
            current_user.organization_id,
            conclusion=conclusion,
        )
        return PaginatedCIRunsResponse(
            items=[self._to_response(r) for r in runs],
            page=page,
            page_size=page_size,
            total=total,
        )

    def get_run(self, current_user: AuthenticatedUser, ci_run_id: UUID) -> CIRunResponse:
        run = self._runs.get_by_id(ci_run_id)
        if run is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": "CI run not found"},
            )
        from shared.repositories import RepositoryRepository

        repo = RepositoryRepository(self._session).get_by_id(run.repository_id)
        if repo is None or repo.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": "CI run not found"},
            )
        return self._to_response(run)

    @staticmethod
    def _to_response(run) -> CIRunResponse:
        return CIRunResponse(
            id=run.id,
            repository_id=run.repository_id,
            workflow_name=run.workflow_name,
            branch=run.branch,
            commit_sha=run.commit_sha,
            conclusion=run.conclusion,
            status_url=run.status_url,
            processing_status=run.processing_status,
            failure_count=run.failure_count,
            ingested_at=run.ingested_at,
            enqueued_at=run.enqueued_at,
            completed_at=run.completed_at,
        )
