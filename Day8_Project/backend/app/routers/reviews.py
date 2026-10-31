from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_review_service
from app.schemas import ErrorOut, ReviewCreate, ReviewCreated, ReviewOut, ReviewPage
from app.services import ReviewService

router = APIRouter(prefix="/reviews", tags=["Reviews"])

PAGE_SIZES = [5, 10]


@router.get("", response_model=ReviewPage, summary="List / search reviews")
def list_reviews(
    employee_id: str | None = Query(None, description="Only this employee's reviews (all periods)"),
    review_period_id: int | None = Query(None, gt=0, description="Only reviews in this period"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, description="Rows per page: 5 or 10", json_schema_extra={"enum": PAGE_SIZES}),
    service: ReviewService = Depends(get_review_service),
):
    """Reviews for the selected filters, newest first, with pagination.

    `average_rating` in the response is the mean over **all** matching reviews,
    e.g. an employee's overall average when filtering by `employee_id`.
    """
    if page_size not in PAGE_SIZES:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "page_size must be 5 or 10")
    return service.search(employee_id, review_period_id, page, page_size)


@router.get(
    "/{review_id}",
    response_model=ReviewOut,
    summary="Get review details",
    responses={404: {"model": ErrorOut}},
)
def get_review(review_id: int, service: ReviewService = Depends(get_review_service)):
    return service.get(review_id)


@router.post(
    "",
    response_model=ReviewCreated,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a review",
    responses={
        409: {"model": ErrorOut, "description": "Employee already reviewed for this period"},
        422: {"description": "Validation error, unknown/inactive employee, unknown/closed period"},
    },
)
def create_review(body: ReviewCreate, service: ReviewService = Depends(get_review_service)):
    return ReviewCreated(message="Review submitted successfully", review=service.create(body))
