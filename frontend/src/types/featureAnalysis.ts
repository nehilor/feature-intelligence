export type AIProcessingState = 'AI_COMPLETE' | 'AI_PARTIAL' | 'MANUAL_REVIEW_REQUIRED'

export type AnalysisContent = {
  summary: string
  underlying_need: string
  theme: string
  customer_impact: string
  urgency: string
  confidence: string
  rationale: string
}

export type AIMetadata = {
  provider: string
  model: string
  prompt_version: string
  used_fallback?: boolean
}

export type FeatureAnalysisResponse = {
  feature_request_id: string
  processing_state: AIProcessingState
  analysis?: AnalysisContent | null
  ai_metadata?: AIMetadata | null
  message?: string | null
}
