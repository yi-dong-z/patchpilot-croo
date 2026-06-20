from calculator import divide


def test_fractional_result_is_preserved():
    assert divide(5, 2) == 2.5


def test_exact_division():
    assert divide(8, 2) == 4


def test_float_input():
    assert divide(7.5, 3) == 2.5
