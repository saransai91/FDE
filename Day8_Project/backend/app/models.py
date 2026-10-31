"""SQLAlchemy ORM models. They mirror db/schema.sql (the source of truth)."""
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    employee_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    department: Mapped[str] = mapped_column(String(100))
    designation: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="Active")


class ReviewPeriod(Base):
    __tablename__ = "review_periods"

    review_period_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    period_type: Mapped[str] = mapped_column(String(20))
    start_date: Mapped[date]
    end_date: Mapped[date]
    status: Mapped[str] = mapped_column(String(10), default="Open")


class PerformanceReview(Base):
    __tablename__ = "performance_reviews"

    review_id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.employee_id"))
    review_period_id: Mapped[int] = mapped_column(ForeignKey("review_periods.review_period_id"))
    quality_rating: Mapped[int] = mapped_column(SmallInteger)
    delivery_rating: Mapped[int] = mapped_column(SmallInteger)
    teamwork_rating: Mapped[int] = mapped_column(SmallInteger)
    average_rating: Mapped[Decimal] = mapped_column(Numeric(3, 2))
    comments: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    employee: Mapped[Employee] = relationship(lazy="joined")
    review_period: Mapped[ReviewPeriod] = relationship(lazy="joined")
