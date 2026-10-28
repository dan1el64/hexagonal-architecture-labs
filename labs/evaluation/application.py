from .domain import EvaluationCase, Verdict, evaluate
from .ports import ResponseProvider


class EvaluateResponses:
    def __init__(self, provider: ResponseProvider):
        self.provider = provider

    def execute(self, cases: list[EvaluationCase]) -> list[Verdict]:
        ids = [case.case_id for case in cases]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate case_id")
        # Fail closed: a provider error propagates, never becomes a passing score.
        return [evaluate(case, self.provider.generate(case)) for case in cases]
