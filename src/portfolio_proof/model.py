from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CheckFailure:
    code: str
    message: str
    path: str
    pain_point: str


@dataclass(frozen=True)
class CheckResults:
    failures: list[CheckFailure] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures

