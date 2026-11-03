"""Typed models separate golden expectations from actual model responses."""

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class GoldenCase:
    case_id: str
    category: str
    question: str
    context: list[str]
    expected_fragments: list[str] = field(default_factory=list)
    forbidden_fragments: list[str] = field(default_factory=list)
    require_refusal: bool = False
    require_citation: bool = False
    block_pii: bool = False
    max_latency_ms: float = 5000


@dataclass(frozen=True)
class ModelAnswer:
    text: str
    latency_ms: float


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    details: str


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    category: str
    passed: bool
    latency_ms: float
    checks: list[CheckResult]
    error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)
