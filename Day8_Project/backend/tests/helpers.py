from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ReviewPeriod


def period_id(db: Session, name: str) -> int:
    return db.scalar(select(ReviewPeriod.review_period_id).where(ReviewPeriod.name == name))
