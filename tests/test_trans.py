import pytest
import logging
import time
@pytest.mark.parametrize("a", range(1, 5))
@pytest.mark.parametrize("b", range(1, 5))
def test_trans(a,b):
    print(f"Testing multiplication: {a} * {b}")
    time.sleep(7)
    assert a+b < a+b+1