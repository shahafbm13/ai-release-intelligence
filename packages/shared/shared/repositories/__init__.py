from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.entities import Organization, Repository, User
from domain.enums import UserRole
from shared.models import OrganizationModel, RepositoryModel, UserModel


def _to_organization(model: OrganizationModel) -> Organization:
    return Organization(
        id=model.id,
        name=model.name,
        slug=model.slug,
        created_at=model.created_at,
    )


def _to_user(model: UserModel) -> User:
    return User(
        id=model.id,
        organization_id=model.organization_id,
        email=model.email,
        role=UserRole(model.role),
        created_at=model.created_at,
    )


def _to_repository(model: RepositoryModel) -> Repository:
    return Repository(
        id=model.id,
        organization_id=model.organization_id,
        full_name=model.full_name,
        default_branch=model.default_branch,
        created_at=model.created_at,
    )


class OrganizationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_slug(self, slug: str) -> Organization | None:
        model = self._session.scalar(
            select(OrganizationModel).where(OrganizationModel.slug == slug)
        )
        return _to_organization(model) if model else None

    def get_by_id(self, org_id: UUID) -> Organization | None:
        model = self._session.get(OrganizationModel, org_id)
        return _to_organization(model) if model else None

    def create(self, name: str, slug: str) -> Organization:
        model = OrganizationModel(name=name, slug=slug)
        self._session.add(model)
        self._session.flush()
        return _to_organization(model)


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_email(self, email: str) -> tuple[User, str] | None:
        model = self._session.scalar(select(UserModel).where(UserModel.email == email))
        if model is None:
            return None
        return _to_user(model), model.password_hash

    def get_by_id(self, user_id: UUID) -> User | None:
        model = self._session.get(UserModel, user_id)
        return _to_user(model) if model else None

    def create(
        self,
        organization_id: UUID,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.VIEWER,
    ) -> User:
        model = UserModel(
            organization_id=organization_id,
            email=email,
            password_hash=password_hash,
            role=role.value,
        )
        self._session.add(model)
        self._session.flush()
        return _to_user(model)


class RepositoryRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_by_organization(self, organization_id: UUID) -> list[Repository]:
        models = self._session.scalars(
            select(RepositoryModel)
            .where(RepositoryModel.organization_id == organization_id)
            .order_by(RepositoryModel.full_name)
        ).all()
        return [_to_repository(m) for m in models]

    def create(
        self,
        organization_id: UUID,
        full_name: str,
        default_branch: str = "main",
    ) -> Repository:
        model = RepositoryModel(
            organization_id=organization_id,
            full_name=full_name,
            default_branch=default_branch,
        )
        self._session.add(model)
        self._session.flush()
        return _to_repository(model)

    def get_by_id(self, repository_id: UUID) -> Repository | None:
        model = self._session.get(RepositoryModel, repository_id)
        return _to_repository(model) if model else None

    def get_by_full_name(self, full_name: str) -> Repository | None:
        model = self._session.scalar(
            select(RepositoryModel).where(RepositoryModel.full_name == full_name)
        )
        return _to_repository(model) if model else None
