"""Request validation rules (no DB needed)."""
import pytest
from pydantic import ValidationError

from app.schemas import ReviewCreate

VALID = dict(employee_id="EMP101", review_period_id=1, quality_rating=3,
             delivery_rating=4, teamwork_rating=5, comments="Good work")


def test_valid_payload():
    assert ReviewCreate(**VALID).comments == "Good work"


@pytest.mark.parametrize("field", ["quality_rating", "delivery_rating", "teamwork_rating"])
@pytest.mark.parametrize("value", [0, 6, -1])
def test_ratings_must_be_between_1_and_5(field, value):
    with pytest.raises(ValidationError):
        ReviewCreate(**{**VALID, field: value})


@pytest.mark.parametrize("comments", ["", "   ", "\n\t"])
def test_comments_are_mandatory(comments):
    with pytest.raises(ValidationError, match="Comments are mandatory"):
        ReviewCreate(**{**VALID, "comments": comments})


def test_comments_max_length():
    with pytest.raises(ValidationError):
        ReviewCreate(**{**VALID, "comments": "x" * 2001})


@pytest.mark.parametrize("field", list(VALID))
def test_all_fields_required(field):
    data = dict(VALID)
    data.pop(field)
    with pytest.raises(ValidationError):
        ReviewCreate(**data)
