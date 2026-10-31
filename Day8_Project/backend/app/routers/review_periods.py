from fastapi import APIRouter, Depends

from app.dependencies import get_review_period_service
from app.schemas import ReviewPeriodOut
from app.services import ReviewPeriodService

router = APIRouter(prefix="/review-periods", tags=["Review Periods"])


@router.get("", response_model=list[ReviewPeriodOut], summary="List review periods")
def list_review_periods(service: ReviewPeriodService = Depends(get_review_period_service)):
    """Master data for the review period dropdown, newest first."""
    return service.list()
