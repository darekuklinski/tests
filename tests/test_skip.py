import pytest

@pytest.mark.skip(reason="This test is skipped intentionally.")
@pytest.mark.parametrize("a", range(1,32))
@pytest.mark.parametrize("b", range(1,32))
def test_skip(a,b):
    assert True