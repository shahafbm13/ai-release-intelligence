"""AI classification eval suite (rules baseline — no live API keys)."""

import pytest

from tests.evals.runner import load_cases, run_eval

pytestmark = pytest.mark.eval


def test_eval_dataset_has_ten_cases():
    cases = load_cases()
    assert len(cases) == 10


def test_classification_eval_pass_rate():
    report = run_eval()
    assert report.total_cases == 10
    assert report.pass_rate_percent >= 70.0, (
        f"Eval pass rate {report.pass_rate_percent}% below 70% target"
    )
    assert report.passed, (
        "Failed cases: "
        + ", ".join(result.case_id for result in report.results if not result.passed)
    )
