import unittest
from labs.evaluation.adapters import FixtureProvider, load_dataset
from labs.evaluation.application import EvaluateResponses
from labs.evaluation.domain import EvaluationCase, evaluate


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.case = EvaluationCase("one", "Describe validation", ("validate", "plan"), ("disable encryption",))

    def test_case_insensitive_rubric_accepts_required_terms(self):
        self.assertTrue(evaluate(self.case, "VALIDATE then PLAN").passed)

    def test_missing_terms_explain_rejection(self):
        result = evaluate(self.case, "validate")
        self.assertFalse(result.passed)
        self.assertEqual(("plan",), result.missing)

    def test_forbidden_term_rejects_otherwise_complete_answer(self):
        result = evaluate(self.case, "validate and plan; disable encryption")
        self.assertFalse(result.passed)
        self.assertEqual(("disable encryption",), result.forbidden)

    def test_empty_response_is_rejected(self):
        self.assertFalse(evaluate(self.case, "").passed)

    def test_duplicate_cases_fail_before_provider_call(self):
        with self.assertRaises(ValueError):
            EvaluateResponses(FixtureProvider({})).execute([self.case, self.case])

    def test_missing_fixture_is_error_not_a_pass(self):
        with self.assertRaises(KeyError):
            EvaluateResponses(FixtureProvider({})).execute([self.case])

    def test_provider_can_be_replaced_without_changing_use_case(self):
        class AnotherProvider:
            def generate(self, case):
                return "validate then plan"
        self.assertTrue(EvaluateResponses(AnotherProvider()).execute([self.case])[0].passed)

    def test_empty_rubric_is_invalid(self):
        with self.assertRaises(ValueError):
            EvaluationCase("empty", "prompt", ())

    def test_synthetic_dataset_has_known_positive_and_negative_cases(self):
        cases, provider = load_dataset("data/evaluation-cases.json")
        results = EvaluateResponses(provider).execute(cases)
        self.assertEqual([True, False, False], [result.passed for result in results])
