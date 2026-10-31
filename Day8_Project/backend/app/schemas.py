"""Pydantic request/response models (the frozen API contract)."""
from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

Rating = Annotated[int, Field(ge=1, le=5, description="Rating from 1 (lowest) to 5 (highest)")]


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: str = Field(examples=["EMP101"])
    name: str = Field(examples=["John Smith"])
    department: str = Field(examples=["Engineering"])
    designation: str = Field(examples=["Senior Developer"])
    email: str = Field(examples=["john.smith@example.com"])
    status: str = Field(examples=["Active"])


class ReviewPeriodOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    review_period_id: int = Field(examples=[2])
    name: str = Field(examples=["H1 2026"])
    period_type: str = Field(examples=["Half-Yearly"])
    start_date: date
    end_date: date
    status: str = Field(examples=["Open"])


class ReviewCreate(BaseModel):
    employee_id: str = Field(min_length=1, max_length=20, examples=["EMP102"])
    review_period_id: int = Field(gt=0, examples=[3])
    quality_rating: Rating
    delivery_rating: Rating
    teamwork_rating: Rating
    comments: str = Field(max_length=2000, examples=["Delivered all sprint stories on time."])

    @field_validator("comments")
    @classmethod
    def comments_required(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Comments are mandatory")
        return v


class ReviewOut(BaseModel):
    review_id: int
    employee_id: str
    employee_name: str
    department: str
    designation: str
    review_period_id: int
    review_period_name: str
    period_type: str
    quality_rating: int
    delivery_rating: int
    teamwork_rating: int
    average_rating: float = Field(description="(quality + delivery + teamwork) / 3, 2 decimals")
    comments: str
    created_at: datetime


class ReviewCreated(BaseModel):
    message: str = Field(examples=["Review submitted successfully"])
    review: ReviewOut


class ReviewPage(BaseModel):
    items: list[ReviewOut]
    total: int = Field(description="Total reviews matching the filters")
    page: int
    page_size: int
    total_pages: int
    average_rating: float | None = Field(
        description="Mean of average_rating over ALL reviews matching the filters (not just this page)"
    )


class ErrorOut(BaseModel):
    detail: str
