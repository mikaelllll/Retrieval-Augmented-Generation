export type DocumentStatus = 'queued' | 'processing' | 'ready' | 'failed'

export interface DocumentRecord {
  id: string
  filename: string
  size_bytes: number
  status: DocumentStatus
  page_count: number | null
  chunk_count: number
  error_message: string | null
  created_at: string
}

export interface Source {
  document_id: string
  filename: string
  page_number: number
  content: string
  similarity: number
  citation: string
}

export interface Answer {
  answer: string
  status: string
  sources: Source[]
  model: string
  retrieval_ms: number
  generation_ms: number
}

