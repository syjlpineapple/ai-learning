
"""
本节课主要学习单元测试，Mock
"""
from unittest.mock import Mock





user = Mock()

user.id = 1
user.get_email.return_value = "aaa@gmail.com"

print(user.id)
print(user.get_email())


def add(a:int,b:int) -> int:
    return a+b

def test_add():
    assert add(1,2) == 3