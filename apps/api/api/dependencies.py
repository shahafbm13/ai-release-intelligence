from collections.abc import Generator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from api.deps import AuthenticatedUser
from api.services.auth_service import AuthService
from api.services.organization_service import OrganizationService
from shared.config import get_settings
from shared.database import get_session_factory
from shared.repositories import UserRepository
from shared.security import decode_access_token

security = HTTPBearer(auto_error=False)
_session_factory = get_session_factory()


def get_db_session() -> Generator[Session, None, None]:
    session = _session_factory()
    try:
        yield session
    finally:
        session.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    session: Session = Depends(get_db_session),
) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Missing bearer token"},
        )
    settings = get_settings()
    try:
        payload = decode_access_token(credentials.credentials, settings.jwt_secret)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Invalid or expired token"},
        ) from exc

    user = UserRepository(session).get_by_id(UUID(payload["sub"]))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "User not found"},
        )
    return AuthenticatedUser(
        user_id=user.id,
        organization_id=user.organization_id,
        email=user.email,
        role=user.role.value,
    )


DbSession = Annotated[Session, Depends(get_db_session)]
CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]


def get_auth_service(session: DbSession) -> AuthService:
    return AuthService(session)


def get_org_service(session: DbSession) -> OrganizationService:
    return OrganizationService(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
OrgServiceDep = Annotated[OrganizationService, Depends(get_org_service)]
