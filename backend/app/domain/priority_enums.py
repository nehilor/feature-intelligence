from enum import Enum


class StrategicAlignment(str, Enum):
    UNKNOWN = "UNKNOWN"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class PriorityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class EvidenceCompleteness(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"


class ProductDecisionType(str, Enum):
    APPROVED = "APPROVED"
    OVERRIDDEN = "OVERRIDDEN"
    DEFERRED = "DEFERRED"
    REJECTED = "REJECTED"


class ReviewerPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
