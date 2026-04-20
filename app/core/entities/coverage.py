from dataclasses import dataclass
from enum import Enum


class CoverageStatus(Enum):
    COVERED = "covered"
    NOT_COVERED = "not_covered"
    UNKNOWN = "unknown"


@dataclass
class CoverageResult:
    status: CoverageStatus
    has_delivery: bool