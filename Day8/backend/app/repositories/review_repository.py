from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.errors import ConflictError
from app.models import PerformanceReview

DUPLICATE_CONSTRAINT = "uq_review_employee_period"


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _filtered(stmt: Select, period_id: int | None, employee_id: int | None) -> Select:
        if period_id is not None:
            stmt = stmt.where(PerformanceReview.period_id == period_id)
        if employee_id is not None:
            stmt = stmt.where(PerformanceReview.employee_id == employee_id)
        return stmt

    def list(
        self,
        period_id: int | None = None,
        employee_id: int | None = None,
        offset: int = 0,
        limit: int = 5,
    ) -> list[PerformanceReview]:
        stmt = self._filtered(select(PerformanceReview), period_id, employee_id)
        stmt = stmt.order_by(PerformanceReview.created_at.desc(), PerformanceReview.id.desc())
        return list(self.db.scalars(stmt.offset(offset).limit(limit)))

    def count(self, period_id: int | None = None, employee_id: int | None = None) -> int:
        stmt = self._filtered(select(func.count(PerformanceReview.id)), period_id, employee_id)
        return self.db.scalar(stmt) or 0

    def exists_for(self, employee_id: int, period_id: int) -> bool:
        stmt = select(PerformanceReview.id).where(
            PerformanceReview.employee_id == employee_id,
            PerformanceReview.period_id == period_id,
        )
        return self.db.scalar(stmt) is not None

    def create(self, review: PerformanceReview) -> PerformanceReview:
        self.db.add(review)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            # A concurrent insert can still hit the unique constraint after exists_for() passed
            if DUPLICATE_CONSTRAINT in str(exc.orig):
                raise ConflictError("A review already exists for this employee and period") from exc
            raise
        self.db.refresh(review)
        return review
