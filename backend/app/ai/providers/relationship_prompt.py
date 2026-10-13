from typing import Optional

from app.ai.prompts.relationship_classification_v1 import UNDERLYING_NEED_LINE, USER_TEMPLATE
from app.ai.providers.relationship_base import RelationshipRequestContext


def _underlying_block(value: Optional[str]) -> str:
    if value and value.strip():
        return UNDERLYING_NEED_LINE.format(value=value.strip())
    return ""


def format_relationship_user_message(
    target: RelationshipRequestContext,
    candidate: RelationshipRequestContext,
) -> str:
    return USER_TEMPLATE.format(
        target_title=target.title,
        target_description=target.description,
        target_underlying_need_block=_underlying_block(target.underlying_need),
        candidate_title=candidate.title,
        candidate_description=candidate.description,
        candidate_underlying_need_block=_underlying_block(candidate.underlying_need),
    )
