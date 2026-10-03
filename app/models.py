"""Data models: the shape of our test cases."""
from typing import Literal

from pydantic import BaseModel,Field

class TestCase(BaseModel):
    __test__ = False  # tell pytest this is not a test class
    title: str
    steps: list[str]
    expected_result: str
    priority: Literal["High","Medium","Low"]


class TestSuite(BaseModel):
    __test__ = False  # tell pytest this is not a test class
    test_cases: list[TestCase]


class GenerateRequest(BaseModel):
    requirement: str = Field(min_length=1, max_length=5000)
    max_cases: int = Field(default=3, ge=1, le=10)


# ------ RAG: documents and retrieval ------


class DocumentIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    text: str = Field(min_length=1, max_length=200_000)


class DocumentOut(BaseModel):
    doc_id: str
    title: str
    chunk_count: int


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    top_k: int = Field(default=3, ge=1, le=10)


class RetrievedChunk(BaseModel):
    id: str
    text: str
    score: float