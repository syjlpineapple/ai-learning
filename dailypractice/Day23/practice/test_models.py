import pytest
from pydantic import ValidationError

from dailypractice.Day23.practice.user_model import User


@pytest.mark.parametrize(
    "age,expected",
    [
        (18, True),
        (0, True),
        (120, True),
        (-1, False),
        (121, False)
    ]
)

def test_model(age, expected):
    if expected:
        user = User(
            name="jack",
            age=age,
            email="jack@gmail.com"
        )
        assert user.age == age
    else:
        with pytest.raises(ValidationError):
            User(
                name="jack",
                age=age,
                email="jack@gmail.com"
            )
