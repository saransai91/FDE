from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_review_period_service
from app.schemas.review_period import PeriodStatus, ReviewPeriodOut
from app.services.review_period_service import ReviewPeriodService

router = APIRouter(prefix="/review-periods", tags=["Review Periods"])


@router.get("", response_model=list[ReviewPeriodOut], summary="Get list of review periods")
def list_review_periods(
    service: Annotated[ReviewPeriodService, Depends(get_review_period_service)],
    status: PeriodStatus | None = None,
):
    return service.list_periods(status)
