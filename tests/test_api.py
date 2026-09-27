"""API tests: fast, free and automatic. They run the app without a real service."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import TestSuite

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_generate_returns_requested_number_of_cases():
    r = client.post("/generate", json={"requirement": "Account locks after 5 failed logins", "max_cases": 2})
    assert r.status_code == 200
    suite = TestSuite.model_validate(r.json())
    assert len(suite.test_cases) == 2


def test_generate_defaults_to_three_cases():
    r = client.post("/generate", json={"requirement": "Login"})
    assert len(r.json()["test_cases"]) == 3


@pytest.mark.parametrize("body", [
    {"requirement": ""},                        # empty
    {},                                         # missing
    {"requirement": "Login", "max_cases": 0},   # below_minimum
    {"requirement": "Login", "max_cases": 11},  # above maximum
    {"requirement": "x" * 50001},               # too long
])
def test_invalid_input_is_rejected(body):
    assert client.post("/generate", json=body).status_code == 422