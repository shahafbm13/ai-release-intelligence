"""Classification eval runner and report generator."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from shared.ai.rule_classifier import classify_with_rules
from shared.ai.schemas import ClassificationOutput, FailureContext

DATASET_VERSION = "v1"
CASES_PATH = Path(__file__).resolve().parent / "data" / DATASET_VERSION / "cases.json"
DEFAULT_REPORT_DIR = Path(__file__).resolve().parents[2] / "reports"


@dataclass
class EvalCase:
    id: str
    description: str
    input: dict
    expected_category: str
    acceptable_categories: list[str]
    expect_insufficient_information: bool
    disallowed_claims: list[str]


@dataclass
class EvalCaseResult:
    case_id: str
    description: str
    passed: bool
    expected_category: str
    actual_category: str
    insufficient_information: bool
    expect_insufficient_information: bool
    provider: str
    failures: list[str]


@dataclass
class EvalReport:
    dataset_version: str
    generated_at: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate_percent: float
    results: list[EvalCaseResult]

    @property
    def passed(self) -> bool:
        return self.failed_cases == 0


def load_cases(path: Path = CASES_PATH) -> list[EvalCase]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [EvalCase(**item) for item in raw]


def _check_disallowed_claims(output: ClassificationOutput, disallowed: list[str]) -> list[str]:
    haystack = " ".join(
        [output.summary, output.likely_cause, output.suggested_action]
    ).lower()
    violations = []
    for claim in disallowed:
        if claim.lower() in haystack:
            violations.append(f"disallowed claim present: {claim!r}")
    return violations


def evaluate_case(case: EvalCase) -> EvalCaseResult:
    context = FailureContext.model_validate(case.input)
    output = classify_with_rules(context)
    failures: list[str] = []

    actual_category = output.category.value
    acceptable = {case.expected_category, *case.acceptable_categories}
    if actual_category not in acceptable:
        failures.append(
            f"category mismatch: expected one of {sorted(acceptable)}, got {actual_category!r}"
        )

    if output.insufficient_information != case.expect_insufficient_information:
        failures.append(
            "insufficient_information mismatch: "
            f"expected {case.expect_insufficient_information}, got {output.insufficient_information}"
        )

    failures.extend(_check_disallowed_claims(output, case.disallowed_claims))

    if not output.summary.strip():
        failures.append("summary must not be empty")

    if not (0.0 <= output.confidence <= 1.0):
        failures.append(f"confidence out of range: {output.confidence}")

    return EvalCaseResult(
        case_id=case.id,
        description=case.description,
        passed=len(failures) == 0,
        expected_category=case.expected_category,
        actual_category=actual_category,
        insufficient_information=output.insufficient_information,
        expect_insufficient_information=case.expect_insufficient_information,
        provider="rules",
        failures=failures,
    )


def run_eval(cases: list[EvalCase] | None = None) -> EvalReport:
    cases = cases or load_cases()
    results = [evaluate_case(case) for case in cases]
    passed = sum(1 for result in results if result.passed)
    total = len(results)
    return EvalReport(
        dataset_version=DATASET_VERSION,
        generated_at=datetime.now(tz=UTC).isoformat(),
        total_cases=total,
        passed_cases=passed,
        failed_cases=total - passed,
        pass_rate_percent=round((passed / total) * 100, 2) if total else 0.0,
        results=results,
    )


def render_markdown(report: EvalReport) -> str:
    lines = [
        "# Classification Eval Report",
        "",
        f"- **Dataset:** {report.dataset_version}",
        f"- **Generated:** {report.generated_at}",
        f"- **Pass rate:** {report.pass_rate_percent}% ({report.passed_cases}/{report.total_cases})",
        "",
        "## Summary",
        "",
    ]
    if report.passed:
        lines.append("All eval cases passed.")
    else:
        lines.append(f"{report.failed_cases} case(s) failed.")

    lines.extend(["", "## Results", ""])
    for result in report.results:
        status = "PASS" if result.passed else "FAIL"
        lines.append(f"### {result.case_id} — {status}")
        lines.append("")
        lines.append(result.description)
        lines.append("")
        lines.append(
            f"- Expected category: `{result.expected_category}`"
            f" → actual: `{result.actual_category}`"
        )
        lines.append(
            f"- Insufficient info: expected `{result.expect_insufficient_information}`,"
            f" got `{result.insufficient_information}`"
        )
        lines.append(f"- Provider: `{result.provider}`")
        if result.failures:
            lines.append("- Failures:")
            for failure in result.failures:
                lines.append(f"  - {failure}")
        lines.append("")

    return "\n".join(lines)


def write_report(report: EvalReport, output_dir: Path = DEFAULT_REPORT_DIR) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "eval-report.json"
    md_path = output_dir / "eval-report.md"

    payload = {
        "dataset_version": report.dataset_version,
        "generated_at": report.generated_at,
        "total_cases": report.total_cases,
        "passed_cases": report.passed_cases,
        "failed_cases": report.failed_cases,
        "pass_rate_percent": report.pass_rate_percent,
        "results": [asdict(result) for result in report.results],
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path


def main() -> None:
    report = run_eval()
    json_path, md_path = write_report(report)
    print(f"Eval pass rate: {report.pass_rate_percent}% ({report.passed_cases}/{report.total_cases})")
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {md_path}")
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
