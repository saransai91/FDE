"""Business rules. Routers call services; services call repositories."""
import math
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy.exc import IntegrityError

from app.errors import BusinessRuleError, ConflictError, NotFoundError
from app.models import Employee, PerformanceReview, ReviewPeriod
from app.repositories import EmployeeRepository, ReviewPeriodRepository, ReviewRepository
from app.schemas import ReviewCreate, ReviewOut, ReviewPage

TWO_PLACES = Decimal("0.01")


def round2(value: Decimal) -> Decimal:
    return Decimal(value).quantize(TWO_PLACES, ROUND_HALF_UP)


def calculate_average(quality: int, delivery: int, teamwork: int) -> Decimal:
    """Average rating = sum of the 3 rating parameters / 3, rounded half-up to 2 decimals."""
    return round2(Decimal(quality + delivery + teamwork) / Decimal(3))


def to_review_out(r: PerformanceReview) -> ReviewOut:
    return ReviewOut(
        review_id=r.review_id,
        employee_id=r.employee_id,
        employee_name=r.employee.name,
        department=r.employee.department,
        designation=r.employee.designation,
        review_period_id=r.review_period_id,
        review_period_name=r.review_period.name,
        period_type=r.review_period.period_type,
        quality_rating=r.quality_rating,
        delivery_rating=r.delivery_rating,
        teamwork_rating=r.teamwork_rating,
        average_rating=float(r.average_rating),
        comments=r.comments,
        created_at=r.created_at,
    )


class EmployeeService:
    def __init__(self, employees: EmployeeRepository):
        self.employees = employees

    def list(self) -> list[Employee]:
        return self.employees.list()

    def get(self, employee_id: str) -> Employee:
        employee = self.employees.get(employee_id)
        if employee is None:
            raise NotFoundError(f"Employee {employee_id} not found")
        return employee


class ReviewPeriodService:
    def __init__(self, periods: ReviewPeriodRepository):
        self.periods = periods

    def list(self) -> list[ReviewPeriod]:
        return self.periods.list()


class ReviewService:
    def __init__(
        self,
        reviews: ReviewRepository,
        employees: EmployeeRepository,
        periods: ReviewPeriodRepository,
    ):
        self.reviews = reviews
        self.employees = employees
        self.periods = periods

    def search(
        self, employee_id: str | None, review_period_id: int | None, page: int, page_size: int
    ) -> ReviewPage:
        total, avg = self.reviews.stats(employee_id, review_period_id)
        items = self.reviews.search(employee_id, review_period_id, (page - 1) * page_size, page_size)
        return ReviewPage(
            items=[to_review_out(r) for r in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size),
            average_rating=float(round2(avg)) if avg is not None else None,
        )

    def get(self, review_id: int) -> ReviewOut:
        review = self.reviews.get(review_id)
        if review is None:
            raise NotFoundError(f"Review {review_id} not found")
        return to_review_out(review)

    def create(self, data: ReviewCreate) -> ReviewOut:
        employee = self.employees.get(data.employee_id)
        if employee is None:
            raise BusinessRuleError(f"Employee {data.employee_id} does not exist")
        if employee.status != "Active":
            raise BusinessRuleError(f"Employee {data.employee_id} is not active")

        period = self.periods.get(data.review_period_id)
        if period is None:
            raise BusinessRuleError(f"Review period {data.review_period_id} does not exist")
        if period.status != "Open":
            raise BusinessRuleError(f"Review period {period.name} is closed")

        duplicate = f"{employee.name} already has a review for {period.name}"
        if self.reviews.exists(data.employee_id, data.review_period_id):
            raise ConflictError(duplicate)

        review = PerformanceReview(
            employee_id=data.employee_id,
            review_period_id=data.review_period_id,
            quality_rating=data.quality_rating,
            delivery_rating=data.delivery_rating,
            teamwork_rating=data.teamwork_rating,
            average_rating=calculate_average(data.quality_rating, data.delivery_rating, data.teamwork_rating),
            comments=data.comments,
        )
        try:
            saved = self.reviews.add(review)
        except IntegrityError as exc:  # two requests raced past the exists() check
            raise ConflictError(duplicate) from exc
        return to_review_out(saved)
