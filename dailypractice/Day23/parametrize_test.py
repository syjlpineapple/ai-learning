"""
参数化测试
"""
import pytest


def validate_age(age:int) -> bool:
    return 0 <= age <= 120


@pytest.mark.parametrize(
    "age,expected",
    [
        (18,True),
        (0,True),
        (120,True)
    ]
)
def test_validate_age(age,expected):
    assert validate_age(age) is expected