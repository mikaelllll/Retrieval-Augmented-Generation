import type { Answer, DocumentRecord } from './types'

const workspaceId = (() => {
  const existing = localStorage.getItem('rag-workspace-id')
  if (existing) return existing
  const created = crypto.randomUUID()
  localStorage.setItem('rag-workspace-id', created)
  return created
})()

async function request<T>(path: string, init: RequestInit = {}, geminiKey?: string): Promise<T> {
  const headers = new Headers(init.headers)
  headers.set('X-Workspace-ID', workspaceId)
  if (geminiKey) headers.set('X-Gemini-API-Key', geminiKey)
  const response = await fetch(`/api/v1${path}`, { ...init, headers })
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(typeof body.detail === 'string' ? body.detail : 'Request failed')
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export const api = {
  documents: () => request<DocumentRecord[]>('/documents'),
  upload: (file: File) => {
    const data = new FormData()
    data.append('file', file)
    return request<DocumentRecord>('/documents', { method: 'POST', body: data })
  },
  remove: (id: string) => request<void>(`/documents/${id}`, { method: 'DELETE' }),
  checkKey: (key: string) =>
    request<{ valid: boolean; model: string; message: string }>('/provider/check', { method: 'POST' }, key),
  ask: (question: string, documentIds: string[], key: string) =>
    request<Answer>(
      '/chat/ask',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, document_ids: documentIds }),
      },
      key,
    ),
}

