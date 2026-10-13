from dataclasses import dataclass
from typing import Sequence


@dataclass
class StructuredOutputReport:
    attempted: int
    valid: int

    @property
    def success_rate(self) -> float:
        if self.attempted == 0:
            return 0.0
        return self.valid / self.attempted


def compute_structured_output_report(valid_flags: Sequence[bool]) -> StructuredOutputReport:
    attempted = len(valid_flags)
    valid = sum(1 for flag in valid_flags if flag)
    return StructuredOutputReport(attempted=attempted, valid=valid)
