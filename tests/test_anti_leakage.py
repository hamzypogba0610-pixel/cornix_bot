from datetime import date
import pytest
from cfcx.data.anti_leakage import assert_no_leakage, LeakageError


def test_ok_when_feature_before_match():
    assert_no_leakage(date(2024, 1, 1), date(2024, 1, 2))


def test_raises_when_feature_same_day():
    with pytest.raises(LeakageError):
        assert_no_leakage(date(2024, 1, 2), date(2024, 1, 2))


def test_raises_when_feature_after_match():
    with pytest.raises(LeakageError):
        assert_no_leakage(date(2024, 1, 3), date(2024, 1, 2))
