"""Unit tests for the pure eligibility calculation engine."""

import pytest
from app.eligibility import check_scheme
from app.models import Profile, SocialCategory, Occupation, IndianState


@pytest.fixture
def sample_scholarship_scheme():
    return {
        "id": "test-scholarship",
        "name": "Test Scholarship",
        "criteria": [
            {"field": "occupation", "op": "==", "value": "student"},
            {"field": "category", "op": "in", "value": ["SC", "ST"]},
            {"field": "annual_income", "op": "<=", "value": 250000},
        ],
    }


def test_all_criteria_met_returns_eligible(sample_scholarship_scheme):
    profile = Profile(
        occupation=Occupation.STUDENT,
        category=SocialCategory.SC,
        annual_income=150000,
    )
    verdict, missing = check_scheme(sample_scholarship_scheme, profile)
    assert verdict == "eligible"
    assert missing == []


def test_income_above_limit_returns_not_eligible(sample_scholarship_scheme):
    profile = Profile(
        occupation=Occupation.STUDENT,
        category=SocialCategory.SC,
        annual_income=300000,
    )
    verdict, missing = check_scheme(sample_scholarship_scheme, profile)
    assert verdict == "not_eligible"
    assert missing == []


def test_missing_income_returns_possibly_eligible(sample_scholarship_scheme):
    profile = Profile(
        occupation=Occupation.STUDENT,
        category=SocialCategory.ST,
        annual_income=None,
    )
    verdict, missing = check_scheme(sample_scholarship_scheme, profile)
    assert verdict == "possibly_eligible"
    assert "annual_income" in missing


def test_wrong_category_returns_not_eligible(sample_scholarship_scheme):
    profile = Profile(
        occupation=Occupation.STUDENT,
        category=SocialCategory.GENERAL,
        annual_income=100000,
    )
    verdict, missing = check_scheme(sample_scholarship_scheme, profile)
    assert verdict == "not_eligible"
    assert missing == []


def test_unknown_operator_raises_value_error():
    invalid_scheme = {
        "id": "test-invalid-op",
        "name": "Invalid Op Scheme",
        "criteria": [
            {"field": "age", "op": "~=", "value": 25},
        ],
    }
    profile = Profile(age=25)
    with pytest.raises(ValueError, match="Unsupported operator '~='"):
        check_scheme(invalid_scheme, profile)


def test_empty_criteria_returns_eligible():
    open_scheme = {
        "id": "test-open",
        "name": "Open Scheme",
        "criteria": [],
    }
    profile = Profile(age=30)
    verdict, missing = check_scheme(open_scheme, profile)
    assert verdict == "eligible"
    assert missing == []


def test_missing_field_when_another_fails_returns_not_eligible(sample_scholarship_scheme):
    # If category fails (General), even though income is missing, verdict is not_eligible
    profile = Profile(
        occupation=Occupation.STUDENT,
        category=SocialCategory.GENERAL,
        annual_income=None,
    )
    verdict, missing = check_scheme(sample_scholarship_scheme, profile)
    assert verdict == "not_eligible"
    assert missing == []


def test_none_profile_returns_possibly_eligible_with_all_criteria_fields(sample_scholarship_scheme):
    verdict, missing = check_scheme(sample_scholarship_scheme, None)
    assert verdict == "possibly_eligible"
    assert set(missing) == {"occupation", "category", "annual_income"}
