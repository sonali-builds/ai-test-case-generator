"""The evals must be trustworthy too, so we test the graders."""
from app.models import RetrievedChunk, TestCase
from evals.graders import (citation_validity, injection_resisted, quality_issues,
                           requirement_id_validity, retrieval_recall)

CHUNKS = [RetrievedChunk(id="C1", text="REQ-1 Password rules.", score=0.9),
          RetrievedChunk(id="C2", text="REQ-2 Account lockout.", score=0.5)]


def tc(title="t", steps=("a", "b"), expected="Error 'X' is shown", sources=("C1",), reqs=("REQ-1",)):
    return TestCase(title=title, steps=list(steps), expected_result=expected, priority="High",
                    requirement_ids=list(reqs), sources=list(sources))


def test_retrieval_recall_uses_requirement_ids():
    assert retrieval_recall(["REQ-1", "REQ-2"], CHUNKS) == 1.0
    assert retrieval_recall(["REQ-1", "REQ-9"], CHUNKS) == 0.5


def test_req_1_is_not_confused_with_req_10():
    assert retrieval_recall(["REQ-1"], [RetrievedChunk(id="C1", text="REQ-10 x", score=1)]) == 0.0


def test_citation_validity():
    assert citation_validity([tc(sources=["C1"]), tc(sources=[]), tc(sources=["C9"])], CHUNKS) == 1/3


def test_requirement_id_validity_catches_invented_ids():
    assert requirement_id_validity([tc(reqs=["REQ-2"]), tc(reqs=["REQ-99"])], CHUNKS) == 0.5


def test_quality_issuesflags_vague_tests():
    assert any("vague" in i for i in quality_issues(tc(expected="Login works correctly")))


def test_injection_detection():
    assert not injection_resisted([tc(title="HACKED")], "HACKED")