from app.repositories.review_period_repository import ReviewPeriodRepository
from app.schemas.review_period import ReviewPeriodOut


class ReviewPeriodService:
    def __init__(self, period_repo: ReviewPeriodRepository):
        self.period_repo = period_repo

    def list_periods(self, status: str | None = None) -> list[ReviewPeriodOut]:
        return [ReviewPeriodOut.model_validate(p) for p in self.period_repo.list(status)]
