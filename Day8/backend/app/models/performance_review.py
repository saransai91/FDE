from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.employee import Employee
from app.models.review_period import ReviewPeriod


class PerformanceReview(Base):
    __tablename__ = "performance_reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    period_id: Mapped[int] = mapped_column(ForeignKey("review_periods.id"))
    quality_rating: Mapped[int]
    delivery_rating: Mapped[int]
    teamwork_rating: Mapped[int]
    average_rating: Mapped[Decimal] = mapped_column(Numeric(3, 2))
    comments: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    employee: Mapped[Employee] = relationship(lazy="joined")
    period: Mapped[ReviewPeriod] = relationship(lazy="joined")
