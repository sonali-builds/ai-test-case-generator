"""Safety net: tests must never call the real (paid) AI."""
import pytest

from app.generator import FakeGenerator, get_generator
from app.main import app


@pytest.fixture(autouse=True)
def use_fake_generator():
    app.dependency_overrides[get_generator] = FakeGenerator
    yield
    app.dependency_overrides.clear()