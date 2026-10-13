from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.domain.enums import FeatureRequestStatus
from app.domain.validation import (
    DESCRIPTION_MAX,
    DESCRIPTION_MIN,
    SUPPORTER_KEY_MAX,
    TITLE_MAX,
    TITLE_MIN,
)


def _trim_required(value: str, field_name: str, min_len: int, max_len: int) -> str:
    trimmed = value.strip()
    if not trimmed:
        raise ValueError(f"{field_name} must not be blank")
    if len(trimmed) < min_len:
        raise ValueError(f"{field_name} must be at least {min_len} characters")
    if len(trimmed) > max_len:
        raise ValueError(f"{field_name} must be at most {max_len} characters")
    return trimmed


class FeatureRequestCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=TITLE_MAX)
    description: str = Field(..., min_length=1, max_length=DESCRIPTION_MAX)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return _trim_required(value, "title", TITLE_MIN, TITLE_MAX)

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        return _trim_required(value, "description", DESCRIPTION_MIN, DESCRIPTION_MAX)


class FeatureRequestResponse(BaseModel):
    id: str
    title: str
    description: str
    status: FeatureRequestStatus
    support_count: int
    created_at: datetime
    updated_at: datetime
    supported_by_current_user: Optional[bool] = None

    model_config = {"from_attributes": True}


class FeatureRequestListResponse(BaseModel):
    items: list[FeatureRequestResponse]
    total: int
    limit: int
    offset: int


class SupportRequest(BaseModel):
    supporter_key: str = Field(..., min_length=1, max_length=SUPPORTER_KEY_MAX)

    @field_validator("supporter_key")
    @classmethod
    def validate_supporter_key(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("supporter_key must not be blank")
        if len(trimmed) > SUPPORTER_KEY_MAX:
            raise ValueError("supporter_key is too long")
        return trimmed


class SupportResponse(BaseModel):
    feature_request_id: str
    supported: bool
    new_support: bool
    support_count: int
