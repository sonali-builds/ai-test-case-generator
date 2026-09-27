"""Unit tests for the fake generator itself."""
from app.generator import FakeGenerator

def test_fake_generator_includes_requirements_in_titles():
    suite = FakeGenerator().generate("Password reset link expires", max_cases=2)
    assert all("Password reset link expires" in tc.title for tc in suite.test_cases)

def test_fake_generator_is_predictable():
    a = FakeGenerator().generate("Login", 3)
    b = FakeGenerator().generate("Login", 3)
    assert a == b