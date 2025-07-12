import pytest
import time

@pytest.mark.parametrize("a", range(1, 32))
@pytest.mark.parametrize("b", range(1,32))
def test_mul(a,b):
    time.sleep(0.3)
    print( a*b < a*b*2)