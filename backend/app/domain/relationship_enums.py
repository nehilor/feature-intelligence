from enum import Enum


class RequestRelationshipType(str, Enum):
    DUPLICATE = "DUPLICATE"
    RELATED = "RELATED"
    DISTINCT = "DISTINCT"


class RelationshipConfidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
