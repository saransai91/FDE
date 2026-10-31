"""Business rules for performance reviews (BR-1..BR-6)."""

from decimal import ROUND_HALF_UP, Decimal

from app.errors import BusinessRuleError, ConflictError
from app.models import PerformanceReview
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.review_period_repository import ReviewPeriodRepository
from app.repositories.review_repository import ReviewRepository
from app.schemas.review import ReviewCreate, ReviewFilters, ReviewOut


def calculate_average(quality: int, delivery: int, teamwork: int) -> Decimal:
    """BR-2: (quality + delivery + teamwork) / 3, rounded to 2 decimals."""
    return (Decimal(quality + delivery + teamwork) / 3).quantize(Decimal("0.01"), ROUND_HALF_UP)


class ReviewService:
    def __init__(
        self,
        review_repo: ReviewRepository,
        employee_repo: EmployeeRepository,
        period_repo: ReviewPeriodRepository,
    ):
        self.review_repo = review_repo
        self.employee_repo = employee_repo
        self.period_repo = period_repo

    def list_reviews(self, filters: ReviewFilters) -> tuple[list[ReviewOut], int]:
        """Returns one page of reviews plus the total count matching the filters."""
        total = self.review_repo.count(filters.period_id, filters.employee_id)
        reviews = self.review_repo.list(
            period_id=filters.period_id,
            employee_id=filters.employee_id,
            offset=(filters.page - 1) * filters.page_size,
            limit=filters.page_size,
        )
        return [ReviewOut.from_model(r) for r in reviews], total

    def create_review(self, data: ReviewCreate) -> ReviewOut:
        employee = self.employee_repo.get(data.employee_id)
        if employee is None:
            raise BusinessRuleError(f"Employee {data.employee_id} does not exist")
        if employee.status != "Active":  # BR-5
            raise BusinessRuleError(f"Employee {employee.employee_id} is {employee.status}")

        period = self.period_repo.get(data.period_id)
        if period is None:
            raise BusinessRuleError(f"Review period {data.period_id} does not exist")
        if period.status != "Open":  # BR-4
            raise BusinessRuleError(f"Review period {period.name} is {period.status}")

        if self.review_repo.exists_for(data.employee_id, data.period_id):  # BR-3
            raise ConflictError("A review already exists for this employee and period")

        review = PerformanceReview(
            employee_id=data.employee_id,
            period_id=data.period_id,
            quality_rating=data.quality_rating,
            delivery_rating=data.delivery_rating,
            teamwork_rating=data.teamwork_rating,
            average_rating=calculate_average(
                data.quality_rating, data.delivery_rating, data.teamwork_rating
            ),
            comments=data.comments,
        )
        return ReviewOut.from_model(self.review_repo.create(review))
