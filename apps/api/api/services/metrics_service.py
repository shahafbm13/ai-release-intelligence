from sqlalchemy.orm import Session

from api.deps import AuthenticatedUser
from api.schemas import MetricsSummaryResponse
from shared.repositories.metrics import MetricsRepository


class MetricsService:
    def __init__(self, session: Session) -> None:
        self._metrics = MetricsRepository(session)

    def get_summary(self, current_user: AuthenticatedUser) -> MetricsSummaryResponse:
        data = self._metrics.summary_for_organization(current_user.organization_id)
        return MetricsSummaryResponse(**data)
