from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    prompt: str
    required_terms: tuple[str, ...]
    forbidden_terms: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.case_id.strip() or not self.prompt.strip():
            raise ValueError("case_id and prompt are required")
        if not self.required_terms or any(not t.strip() for t in self.required_terms + self.forbidden_terms):
            raise ValueError("rubric needs non-empty required terms and no blank terms")


@dataclass(frozen=True)
class Verdict:
    case_id: str
    passed: bool
    missing: tuple[str, ...]
    forbidden: tuple[str, ...]


def evaluate(case: EvaluationCase, response: str) -> Verdict:
    """Transparent substring rubric, not a semantic correctness judge."""
    normalized = response.casefold()
    missing = tuple(term for term in case.required_terms if term.casefold() not in normalized)
    forbidden = tuple(term for term in case.forbidden_terms if term.casefold() in normalized)
    return Verdict(case.case_id, not missing and not forbidden, missing, forbidden)
