"""Input validation rules on the ReviewCreate schema (BR-1, BR-6)."""

import pytest
from pydantic import ValidationError

from app.schemas.review import ReviewCreate

VALID = dict(employee_id=1, period_id=6, quality_rating=4, delivery_rating=5,
             teamwork_rating=4, comments="Good")


def test_valid_payload_strips_comments():
    assert ReviewCreate(**{**VALID, "comments": "  Good  "}).comments == "Good"


@pytest.mark.parametrize("field", ["quality_rating", "delivery_rating", "teamwork_rating"])
@pytest.mark.parametrize("value", [0, 6, -1, 4.5, "4"])
def test_rating_must_be_integer_1_to_5(field, value):
    with pytest.raises(ValidationError):
        ReviewCreate(**{**VALID, field: value})


@pytest.mark.parametrize("comments", ["", "   ", "x" * 2001])
def test_comments_mandatory_and_max_length(comments):
    with pytest.raises(ValidationError):
        ReviewCreate(**{**VALID, "comments": comments})


@pytest.mark.parametrize("field", list(VALID))
def test_all_fields_required(field):
    data = {k: v for k, v in VALID.items() if k != field}
    with pytest.raises(ValidationError):
        ReviewCreate(**data)


def test_client_cannot_send_average_rating():
    with pytest.raises(ValidationError):
        ReviewCreate(**VALID, average_rating=5)
