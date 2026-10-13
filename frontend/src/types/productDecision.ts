import type { PriorityLevel } from './priority'

export type ProductDecisionType = 'APPROVED' | 'OVERRIDDEN' | 'DEFERRED' | 'REJECTED'
export type ReviewerPriority = 'LOW' | 'MEDIUM' | 'HIGH'

export type SystemRecommendationSnapshot = {
  priority_level: PriorityLevel
  total_score: number
  formula_version: string
  demand_score: number
  impact_score: number
  urgency_score: number
  strategic_alignment_score: number
}

export type ProductDecisionResponse = {
  feature_request_id: string
  priority_assessment_id: string
  decision: ProductDecisionType
  reviewer_priority?: ReviewerPriority
  override_reason?: string
  reviewer_note?: string
  system_recommendation_at_decision: SystemRecommendationSnapshot
  created_at: string
  updated_at: string
  message?: string
}

export type ProductDecisionCreate = {
  decision: ProductDecisionType
  reviewer_priority?: ReviewerPriority
  override_reason?: string
  reviewer_note?: string
}
