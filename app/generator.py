"""A fake AI: returns realistic test cases without calling any API."""
from .models import TestCase, TestSuite


class FakeGenerator:
    def generate(self,requirement: str, max_cases: int = 3) -> TestSuite:
        short = requirement.strip()[:50]
        cases = [
            TestCase(
                title=f"[FAKE] Scenario {i + 1}: {short}",
                steps=["Open the feature", f"Perform action {i + 1}"],
                expected_result=f"Result {i + 1} matches the requirement",
                priority="Medium",
            )
            for i in range(max_cases)
        ]
        return TestSuite(test_cases=cases)

def get_generator() -> FakeGenerator:
    return FakeGenerator()