from app.ai.prompts.decision_brief_v1 import USER_TEMPLATE
from app.ai.providers.decision_brief_base import DecisionBriefEvidenceContext


def format_decision_brief_user_message(context: DecisionBriefEvidenceContext) -> str:
    if context.relationship_lines:
        relationship_block = "\n".join(f"- {line}" for line in context.relationship_lines)
    else:
        relationship_block = "- (none persisted)"

    return USER_TEMPLATE.format(
        feature_request_id=context.feature_request_id,
        support_count=context.support_count,
        relationship_signal_count=context.relationship_signal_count,
        formula_version=context.formula_version,
        total_score=context.total_score,
        priority_level=context.priority_level,
        strategic_alignment=context.strategic_alignment,
        evidence_completeness=context.evidence_completeness,
        demand_score=context.demand_score,
        impact_score=context.impact_score,
        urgency_score=context.urgency_score,
        strategic_alignment_score=context.strategic_alignment_score,
        customer_impact_label=context.customer_impact_label,
        urgency_label=context.urgency_label,
        analysis_summary=context.analysis_summary or "(unavailable)",
        underlying_need=context.underlying_need or "(unavailable)",
        theme=context.theme or "(unavailable)",
        relationship_lines=relationship_block,
        title=context.title,
        description=context.description,
    )
