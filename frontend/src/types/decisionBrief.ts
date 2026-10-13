export type DecisionBriefResponse = {
  feature_request_id: string
  priority_assessment_id: string
  problem: string
  evidence_summary: string
  why_it_matters: string
  risks_and_unknowns: string[]
  recommended_next_step: string
  provider?: string
  model?: string
  prompt_version?: string
  created_at?: string
  message?: string
}
