from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response

from app.api.deps import get_review_service
from app.schemas.review import ReviewCreate, ReviewFilters, ReviewOut
from app.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["Reviews"])

ReviewServiceDep = Annotated[ReviewService, Depends(get_review_service)]

ERROR_RESPONSES = {
    409: {"description": "Duplicate review for employee + period"},
    422: {"description": "Invalid input or business rule violation"},
}


@router.get(
    "",
    response_model=list[ReviewOut],
    summary="Get reviews (optional filters, paginated)",
    responses={200: {"headers": {"X-Total-Count": {"description": "Total matching reviews", "schema": {"type": "integer"}}}}},
)
def list_reviews(
    response: Response,
    service: ReviewServiceDep,
    filters: Annotated[ReviewFilters, Query()],
):
    reviews, total = service.list_reviews(filters)
    response.headers["X-Total-Count"] = str(total)
    return reviews


@router.post("", response_model=ReviewOut, status_code=201, summary="Submit a new review", responses=ERROR_RESPONSES)
def create_review(data: ReviewCreate, service: ReviewServiceDep):
    return service.create_review(data)
