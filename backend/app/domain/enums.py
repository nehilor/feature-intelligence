from enum import Enum


class FeatureRequestStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    PLANNED = "PLANNED"
    DECLINED = "DECLINED"
    DELIVERED = "DELIVERED"
