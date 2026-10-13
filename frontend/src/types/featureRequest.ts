export type FeatureRequestStatus =
  | 'SUBMITTED'
  | 'UNDER_REVIEW'
  | 'PLANNED'
  | 'DECLINED'
  | 'DELIVERED'

export type FeatureRequest = {
  id: string
  title: string
  description: string
  status: FeatureRequestStatus
  support_count: number
  created_at: string
  updated_at: string
  supported_by_current_user?: boolean | null
}

export type FeatureRequestListResponse = {
  items: FeatureRequest[]
  total: number
  limit: number
  offset: number
}

export type SupportResponse = {
  feature_request_id: string
  supported: boolean
  new_support: boolean
  support_count: number
}
