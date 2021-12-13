import time

import pytest

from chip8.backends.pysdl import PySDLBackend


def test_throttle():
    """It should take approximately a second for the backend set to 
    60hz to run 60 times in a loop.
    """
    backend = PySDLBackend(60)

    start = time.time()

    for _ in range(0, 60):
        backend.throttle()

    assert 1 == pytest.approx(time.time() - start, 0.1)
