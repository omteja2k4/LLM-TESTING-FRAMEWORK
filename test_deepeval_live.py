"""Optional semantic LLM-as-judge eval. Never runs on key-free CI."""

import os
import pytest


@pytest.mark.live
def test_gemini_faithfulness_and_answer_relevancy():
    if os.getenv("RUN_LIVE_EVAL") != "1":
        pytest.skip("Set RUN_LIVE_EVAL=1 to run cost-bearing live evaluation")
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("Set GOOGLE_API_KEY or GEMINI_API_KEY")
    pytest.importorskip("deepeval")

    from ai_quality.clients import GeminiClient
    from ai_quality.models import GoldenCase
    from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
    from deepeval.test_case import LLMTestCase

    os.environ["GOOGLE_API_KEY"] = api_key
    os.environ["USE_GEMINI_MODEL"] = "1"
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    case = GoldenCase(
        case_id="live_warranty", category="factual",
        question="What is Product A's warranty period?",
        context=["Product A has a warranty of two years."],
        require_citation=True,
    )
    answer = GeminiClient(model=model).answer(case)
    test_case = LLMTestCase(
        input=case.question, actual_output=answer.text,
        retrieval_context=case.context,
    )
    for metric in [
        FaithfulnessMetric(threshold=0.7, model=model, async_mode=False),
        AnswerRelevancyMetric(threshold=0.7, model=model, async_mode=False),
    ]:
        metric.measure(test_case)
        assert metric.is_successful(), f"{type(metric).__name__}: {metric.reason}"
