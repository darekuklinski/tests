import pytest

@pytest.mark.parametrize("a", range(1, 32))
@pytest.mark.parametrize("b", range(1, 32))
def test_xfail(a, b):
    pytest.xfail("This test is expected to fail.")
    assert a + b < a + b + 1