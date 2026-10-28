import json
from pathlib import Path
from .domain import EvaluationCase


class FixtureProvider:
    """Recorded synthetic answers. This adapter does not call a language model."""

    def __init__(self, answers: dict[str, str]):
        if any(not isinstance(value, str) for value in answers.values()):
            raise ValueError("every answer must be a string")
        self.answers = dict(answers)

    def generate(self, case: EvaluationCase) -> str:
        return self.answers[case.case_id]


def load_dataset(path: str) -> tuple[list[EvaluationCase], FixtureProvider]:
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    cases = [EvaluationCase(row["id"], row["prompt"], tuple(row["required"]), tuple(row.get("forbidden", []))) for row in rows]
    ids = [case.case_id for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate case_id")
    return cases, FixtureProvider({row["id"]: row["answer"] for row in rows})
