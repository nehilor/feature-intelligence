export type StrategicAlignment = 'UNKNOWN' | 'LOW' | 'MEDIUM' | 'HIGH'
export type PriorityLevel = 'LOW' | 'MEDIUM' | 'HIGH'
export type EvidenceCompleteness = 'COMPLETE' | 'PARTIAL'

export type DemandBreakdown = {
  score: number
  max_score: number
  support_count: number
  relationship_signal_count: number
}

export type ScoredDimensionBreakdown = {
  value: string
  score: number
  max_score: number
}

export type PriorityBreakdown = {
  demand: DemandBreakdown
  customer_impact: ScoredDimensionBreakdown
  urgency: ScoredDimensionBreakdown
  strategic_alignment: ScoredDimensionBreakdown
}

export type PriorityAssessmentResponse = {
  feature_request_id: string
  priority_level: PriorityLevel
  total_score: number
  formula_version: string
  evidence_completeness: EvidenceCompleteness
  strategic_alignment: StrategicAlignment
  breakdown: PriorityBreakdown
  message?: string
}
