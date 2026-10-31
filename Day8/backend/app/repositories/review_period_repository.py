from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ReviewPeriod


class ReviewPeriodRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, status: str | None = None) -> list[ReviewPeriod]:
        stmt = select(ReviewPeriod).order_by(ReviewPeriod.start_date.desc(), ReviewPeriod.name)
        if status is not None:
            stmt = stmt.where(ReviewPeriod.status == status)
        return list(self.db.scalars(stmt))

    def get(self, period_pk: int) -> ReviewPeriod | None:
        return self.db.get(ReviewPeriod, period_pk)
