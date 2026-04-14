export type FileType = 'image' | 'video' | 'audio' | 'document' | 'unknown'
export type SignalSeverity = 'low' | 'medium' | 'high'

export interface DetectionSignal {
  name: string
  description: string
  severity: SignalSeverity
  score: number
  details?: string
}

export interface MetadataField {
  key: string
  value: string
  suspicious: boolean
  note?: string
}

export interface C2PAResult {
  has_credentials: boolean
  provider?: string
  claim_generator?: string
  signed: boolean
  trusted: boolean
  assertions: string[]
  note: string
}

export interface AnalysisResult {
  job_id: string
  filename: string
  file_type: FileType
  file_size_bytes: number
  mime_type: string

  ai_probability: number
  confidence: number
  verdict: string
  verdict_color: 'red' | 'orange' | 'yellow' | 'green'

  signals: DetectionSignal[]
  metadata: MetadataField[]
  c2pa: C2PAResult

  metadata_score: number
  artifact_score: number
  frequency_score: number
  consistency_score: number

  analysis_duration_ms: number
  analyzed_at: string
  report_available: boolean
}
