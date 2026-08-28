import type { Source } from './types'

export function sourceMatchLabel(source: Source): string {
  if (source.retrieval_method === 'overview') return 'Overview passage'
  return `${Math.round((source.similarity ?? 0) * 100)}% match`
}
