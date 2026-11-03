# LLM Testing Framework — AI Quality Assurance

A compact Python project for **AI quality engineering**. It checks an AI assistant against curated golden cases, detects expected-content regressions, checks citations, refusals, basic PII patterns, and latency, and generates JSON reports. An **optional** DeepEval integration uses Gemini as an LLM judge to score faithfulness and answer relevancy.

> **Evaluation integrity:** The default dataset and responses are **12 synthetic, hand-written examples**. Offline CI results prove that the **test framework** operates as intended, **not** that a real LLM has 100% accuracy or is safe. Run live evaluations and publish measured results before making claims about model quality.

## Features

- **Golden test dataset:** 12 labeled scenarios across factual answers, evidence gaps, prompt injection, privacy, and safety.
- **Negative test suite:** deliberate wrong answers, missing citations, missing refusals, PII leaks, and latency failures are caught by unit tests.
- **Deterministic offline provider:** no key, cloud access or charges needed to run standard tests.
- **Optional live Gemini provider:** calls Gemini REST API with an environment-only API key.
- **Optional DeepEval:** LLM-as-judge faithfulness + answer relevancy metrics (requires separate model calls).
- **Quality reporting:** per-case pass/fail, check details, pass rate, mean latency and p95 latency in a JSON report.
- **Continuous integration:** GitHub Actions automatically runs the offline Pytest suite and uploads a JSON report on pushes and PRs.

## Architecture

```text
Synthetic golden questions + expected behavior
                    |
         Model-under-test adapter
            /             \
 FixtureClient       GeminiClient (live)
            \             /
                ModelAnswer
                    |
       Deterministic quality checks
        /    |       |      |     \
   content  citation refusal  PII  latency
                    |
            JSON report / CI gate
                    |
      Optional DeepEval LLM judge
        faithfulness + relevance
```

**Technical distinctions:** A substring check is **not** proof of factual faithfulness; a numbered citation regex checks **format**, not whether the cited passage supports the claim. Use semantic metrics, human review and adversarial data for meaningful real-world assessments. A regex does not fully establish PII safety.

## Requirements

Python 3.10+ (developed for 3.11).

## Setup and run — no API key needed

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest -m "not live" -v
llm-qa --provider fixture --output reports/evaluation.json
```

The CLI exits with code 1 when any case fails, so it can be used in CI.

## Live Gemini evaluation (may incur cost)

First add an API key in your local environment; **never put it in the repository**.

```bash
# Linux/macOS
export GEMINI_API_KEY="your-key"
export GEMINI_MODEL="gemini-2.5-flash"
llm-qa --provider gemini --output reports/live-report.json
```

On Windows PowerShell: `$env:GEMINI_API_KEY="your-key"`.

The example suite contains adversarial prompts, so some real-model responses will differ. Inspect failed cases rather than blindly weakening thresholds.

## Optional semantic evaluation with DeepEval

DeepEval uses an LLM-as-a-judge for **faithfulness** and **answer relevancy**. Configure a Gemini key for the judge as well. This is **not** part of the no-key CI workflow.

```bash
python -m pip install -e ".[dev,llm]"
export GEMINI_API_KEY="your-key"
export GOOGLE_API_KEY="$GEMINI_API_KEY"
export USE_GEMINI_MODEL=1
export RUN_LIVE_EVAL=1
pytest -m live -v
```

The optional test calls a real Gemini model and runs DeepEval `FaithfulnessMetric` and `AnswerRelevancyMetric`. The test may fail because a model generates an insufficient answer or because the judge is unreliable; these are investigation signals, not absolute ground truth.

## Project structure

```text
src/ai_quality/
  clients.py     # Offline fixture and live Gemini adapters
  models.py      # Typed golden cases and evaluation outputs
  goldens.py     # Golden dataset validation
  checks.py      # Deterministic content, citation, privacy, refusal and latency checks
  runner.py      # Batch execution, failure isolation, JSON-ready results
  cli.py         # CLI entry point with failure exit codes
datasets/
  goldens.json              # 12 synthetic, labeled test scenarios
  fixture_responses.json    # Deterministic sample answers
tests/
  test_golden_regressions.py
  test_failure_detection.py
  test_dataset_validation.py
  test_deepeval_live.py      # Skipped unless explicitly enabled
.github/workflows/quality.yml
```

## How to extend

1. Replace synthetic cases with real, documented, consented benchmark examples.
2. Add expected outputs and rubric criteria for each use case.
3. Connect your own AI service in a new adapter, preserving `answer(case)`.
4. Run repeated live evaluations to handle nondeterminism and save distributions, not only single-run scores.
5. Review DeepEval explanations manually and separate CI deterministic checks from fluctuating LLM-as-judge metrics.
6. Add Playwright / Appium suites as a separate integration when testing web or mobile clients.

## Attribution

This is an independently structured educational implementation of common LLM QA patterns. DeepEval API examples follow the official documentation: https://deepeval.com/docs/metrics-faithfulness and https://deepeval.com/integrations/models/gemini.

## License

MIT.
