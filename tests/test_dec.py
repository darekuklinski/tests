import pytest
import time
@pytest.mark.parametrize("a", range(32))
@pytest.mark.parametrize("b", range(32))
def test_dec(a,b):
    time.sleep(6)
    assert a+b < a+b+1