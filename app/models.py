"""Data models: the shape of our test cases."""
from typing import Literal

from pydantic import BaseModel,Field

class TestCase(BaseModel):
    title: str
    steps: list[str]
    expected_result: str
    priority: Literal["High","Medium","Low"]


class TestSuite(BaseModel):
    test_cases: list[TestCase]


class GenerateRequest(BaseModel):
    requirement: str = Field(min_length=1, max_length=5000)
    max_cases: int = Field(default=3, ge=1, le=10)
