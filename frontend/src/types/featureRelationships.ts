export type RequestRelationshipType = 'DUPLICATE' | 'RELATED' | 'DISTINCT'

export type RelationshipConfidence = 'LOW' | 'MEDIUM' | 'HIGH'

export type RelationshipItem = {
  feature_request_id: string
  title: string
  relationship: RequestRelationshipType
  similarity_score: number
  confidence: RelationshipConfidence
  reason: string
  support_count: number
}

export type RelationshipsResponse = {
  feature_request_id: string
  status: string
  items: RelationshipItem[]
  message?: string | null
}
