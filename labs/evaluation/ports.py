from typing import Protocol
from .domain import EvaluationCase


class ResponseProvider(Protocol):
    def generate(self, case: EvaluationCase) -> str: ...
