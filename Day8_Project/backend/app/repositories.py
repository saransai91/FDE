"""Data access. The only layer that runs queries."""
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Employee, PerformanceReview, ReviewPeriod


class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[Employee]:
        return list(self.db.scalars(select(Employee).order_by(Employee.name)))

    def get(self, employee_id: str) -> Employee | None:
        return self.db.get(Employee, employee_id)


class ReviewPeriodRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[ReviewPeriod]:
        stmt = select(ReviewPeriod).order_by(ReviewPeriod.start_date.desc(), ReviewPeriod.end_date)
        return list(self.db.scalars(stmt))

    def get(self, review_period_id: int) -> ReviewPeriod | None:
        return self.db.get(ReviewPeriod, review_period_id)


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _filters(employee_id: str | None, review_period_id: int | None) -> list:
        conds = []
        if employee_id:
            conds.append(PerformanceReview.employee_id == employee_id)
        if review_period_id:
            conds.append(PerformanceReview.review_period_id == review_period_id)
        return conds

    def search(
        self, employee_id: str | None, review_period_id: int | None, offset: int, limit: int
    ) -> list[PerformanceReview]:
        stmt = (
            select(PerformanceReview)
            .where(*self._filters(employee_id, review_period_id))
            .order_by(PerformanceReview.created_at.desc(), PerformanceReview.review_id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).unique())

    def stats(self, employee_id: str | None, review_period_id: int | None) -> tuple[int, Decimal | None]:
        """Count and mean average_rating over every review matching the filters."""
        stmt = select(func.count(), func.avg(PerformanceReview.average_rating)).where(
            *self._filters(employee_id, review_period_id)
        )
        total, avg = self.db.execute(stmt).one()
        return total, avg

    def get(self, review_id: int) -> PerformanceReview | None:
        return self.db.get(PerformanceReview, review_id)

    def exists(self, employee_id: str, review_period_id: int) -> bool:
        stmt = select(PerformanceReview.review_id).where(
            PerformanceReview.employee_id == employee_id,
            PerformanceReview.review_period_id == review_period_id,
        )
        return self.db.scalar(stmt) is not None

    def add(self, review: PerformanceReview) -> PerformanceReview:
        try:
            self.db.add(review)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        self.db.refresh(review)
        return review
