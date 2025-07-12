import pytest
@pytest.mark.parametrize("a", range(1, 32))
@pytest.mark.parametrize("b", range(1, 32))
def test_fail(a,b):
    assert False