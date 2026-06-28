from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.deps import AuthenticatedUser
from api.schemas import LoginRequest, TokenResponse, UserResponse
from domain.enums import UserRole
from shared.config import get_settings
from shared.repositories import UserRepository
from shared.security import create_access_token, verify_password


class AuthService:
    def __init__(self, session: Session) -> None:
        self._users = UserRepository(session)
        self._settings = get_settings()

    def login(self, request: LoginRequest) -> TokenResponse:
        result = self._users.get_by_email(request.email)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "UNAUTHORIZED", "message": "Invalid email or password"},
            )
        user, password_hash = result
        if not verify_password(request.password, password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "UNAUTHORIZED", "message": "Invalid email or password"},
            )
        token = create_access_token(
            subject=str(user.id),
            organization_id=user.organization_id,
            role=user.role.value,
            secret=self._settings.jwt_secret,
            expires_hours=self._settings.jwt_expire_hours,
        )
        return TokenResponse(access_token=token)

    def get_me(self, current_user: AuthenticatedUser) -> UserResponse:
        return UserResponse(
            id=current_user.user_id,
            email=current_user.email,
            role=current_user.role,
            organization_id=current_user.organization_id,
        )

    def require_role(self, current_user: AuthenticatedUser, *roles: UserRole) -> None:
        if UserRole(current_user.role) not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "Insufficient permissions"},
            )
