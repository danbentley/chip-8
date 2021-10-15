import pytest


@pytest.fixture(autouse=True)
def pygame(monkeypatch):
    """Patch pygame to prevent it from running during testing."""

    def noop(*args, **kwargs):
        ...

    monkeypatch.setattr("pygame.event", noop)
    monkeypatch.setattr("pygame.display.set_mode", noop)
    monkeypatch.setattr("pygame.Surface", noop)
