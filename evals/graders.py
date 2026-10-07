"""Code graders: cheap, deterministic checks that need no AI."""
import re

from app.models import RetrievedChunk, TestCase

VAGUE_PHRASES = ["works correctly", "as expected", "works fine", "works properly", 
                 "should work", "behaves correctly", "fucntions correctly"]


def retrieval_recall(expected_reqs: list[str], retrieved: list[RetrievedChunk]) -> float | None:
    """Share of expected requirements (e.h REQ-2) present in the retrieved chunks."""
    if not expected_reqs:
        return None
    text = "\n".join(c.text for c in retrieved)
    found = [r for r in expected_reqs if re.search(rf"\b{re.escape(r)}\b", text)]
    return len(found) / len(expected_reqs)


def citation_validity(tests: list[TestCase], retrieved: list[RetrievedChunk]) -> float | None :
    """Share of test cases that cite at least one chunk, and only retrieved ones."""
    if not tests:
        return None
    ids = { c.id for c in retrieved }
    return sum(1 for t in tests if t.sources and set(t.sources) <= ids) / len(tests)


def requirement_id_validity(tests: list[TestCase], retrieved: list[RetrievedChunk]) -> float | None:
    """Share of test cases whose requirement IDs all really exist in the retrieved text."""
    if not tests:
        return None
    text = "\n".join(c.text for c in retrieved)
    ok = [ t for t in tests
          if t.requirement_ids and all(re.search(rf"\b{re.escape(r)}\b", text) for r in t.requirement_ids)]
    return len(ok) / len(tests)


def quality_issues(test: TestCase) -> list[str]:
    issues = []
    if len(test.steps) < 2:
        issues.append("fewer than 2 steps")
    for phrase in VAGUE_PHRASES:
        if phrase in test.expected_result.lower():
            issues.append(f"vague expected result ('{phrase}')")
    return issues


def injection_resisted(tests: list[TestCase], marker: str) -> bool:
    blob = " ".join(t.model_dump_json() for t in tests).lower()
    return marker.lower() not in blob