"""Run evaluations and produce a JSON report suitable for CI artifacts."""

from datetime import datetime, timezone
from .checks import evaluate_case
from .clients import AnswerClient
from .models import CaseResult, GoldenCase


def run_suite(cases: list[GoldenCase], client: AnswerClient) -> dict:
    results = []
    for case in cases:
        try:
            answer = client.answer(case)
            checks = evaluate_case(case, answer)
            results.append(CaseResult(
                case_id=case.case_id,
                category=case.category,
                passed=all(check.passed for check in checks),
                latency_ms=round(answer.latency_ms, 2),
                checks=checks,
            ))
        except Exception as exc:
            # Expose exception class only, not secret-bearing exception text.
            results.append(CaseResult(
                case_id=case.case_id, category=case.category,
                passed=False, latency_ms=0.0, checks=[],
                error=f"{type(exc).__name__} while invoking the model",
            ))

    passed = sum(result.passed for result in results)
    latencies = sorted(result.latency_ms for result in results if result.error is None)
    p95_idx = max(0, (len(latencies) * 95 + 99) // 100 - 1)
    summary = {
        "total_cases": len(results),
        "passed_cases": passed,
        "failed_cases": len(results) - passed,
        "pass_rate": round(passed / len(results), 4) if results else 0,
        "mean_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else None,
        "p95_latency_ms": round(latencies[p95_idx], 2) if latencies else None,
    }
    return {
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "results": [result.to_dict() for result in results],
    }
