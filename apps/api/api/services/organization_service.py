from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.deps import AuthenticatedUser
from api.schemas import OrganizationResponse, RepositoryCreateRequest, RepositoryResponse
from shared.repositories import OrganizationRepository, RepositoryRepository


class OrganizationService:
    def __init__(self, session: Session) -> None:
        self._orgs = OrganizationRepository(session)
        self._repos = RepositoryRepository(session)

    def get_my_organization(self, current_user: AuthenticatedUser) -> OrganizationResponse:
        org = self._orgs.get_by_id(current_user.organization_id)
        if org is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": "Organization not found"},
            )
        return OrganizationResponse(id=org.id, name=org.name, slug=org.slug)

    def list_repositories(self, current_user: AuthenticatedUser) -> list[RepositoryResponse]:
        repos = self._repos.list_by_organization(current_user.organization_id)
        return [
            RepositoryResponse(
                id=r.id,
                organization_id=r.organization_id,
                full_name=r.full_name,
                default_branch=r.default_branch,
            )
            for r in repos
        ]

    def create_repository(
        self,
        current_user: AuthenticatedUser,
        request: RepositoryCreateRequest,
    ) -> RepositoryResponse:
        repo = self._repos.create(
            organization_id=current_user.organization_id,
            full_name=request.full_name,
            default_branch=request.default_branch,
        )
        return RepositoryResponse(
            id=repo.id,
            organization_id=repo.organization_id,
            full_name=repo.full_name,
            default_branch=repo.default_branch,
        )

    def get_repository(
        self,
        current_user: AuthenticatedUser,
        repository_id: UUID,
    ) -> RepositoryResponse:
        repo = self._repos.get_by_id(repository_id)
        if repo is None or repo.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": "Repository not found"},
            )
        return RepositoryResponse(
            id=repo.id,
            organization_id=repo.organization_id,
            full_name=repo.full_name,
            default_branch=repo.default_branch,
        )
