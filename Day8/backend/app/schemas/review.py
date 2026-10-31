from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import PerformanceReview

Rating = Annotated[int, Field(ge=1, le=5, strict=True)]  # BR-1: whole numbers 1-5 only


class ReviewCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    employee_id: int = Field(ge=1)
    period_id: int = Field(ge=1)
    quality_rating: Rating
    delivery_rating: Rating
    teamwork_rating: Rating
    comments: str = Field(max_length=2000)

    @field_validator("comments")
    @classmethod
    def comments_not_blank(cls, value: str) -> str:  # BR-6
        value = value.strip()
        if not value:
            raise ValueError("Comments are mandatory")
        return value


class ReviewFilters(BaseModel):
    period_id: int | None = Field(default=None, ge=1)
    employee_id: int | None = Field(default=None, ge=1)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=5, ge=1, le=100)


class ReviewOut(BaseModel):
    id: int
    employee_id: int
    employee_code: str
    employee_name: str
    period_id: int
    period_name: str
    quality_rating: int
    delivery_rating: int
    teamwork_rating: int
    average_rating: float
    comments: str
    created_at: datetime

    @classmethod
    def from_model(cls, review: PerformanceReview) -> "ReviewOut":
        return cls(
            id=review.id,
            employee_id=review.employee_id,
            employee_code=review.employee.employee_id,
            employee_name=review.employee.name,
            period_id=review.period_id,
            period_name=review.period.name,
            quality_rating=review.quality_rating,
            delivery_rating=review.delivery_rating,
            teamwork_rating=review.teamwork_rating,
            average_rating=float(review.average_rating),
            comments=review.comments,
            created_at=review.created_at,
        )
