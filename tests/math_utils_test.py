from math_utils import add

def test_add_two_numbers():
    assert add(2, 3) == 5

def test_add_negative_number():
    assert add(-1, 5) == 4