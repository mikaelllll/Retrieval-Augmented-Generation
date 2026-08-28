import { describe, expect, it } from 'vitest'
import { sourceMatchLabel } from './sourceDisplay'
import type { Source } from './types'

function source(overrides: Partial<Source>): Source {
  return {
    document_id: '00000000-0000-0000-0000-000000000000',
    filename: 'example.pdf',
    page_number: 1,
    content: 'Evidence',
    similarity: 0.28,
    retrieval_method: 'semantic',
    citation: '[S1]',
    ...overrides,
  }
}

describe('sourceMatchLabel', () => {
  it('formats semantic similarity as a rounded percentage', () => {
    expect(sourceMatchLabel(source({ similarity: 0.284 }))).toBe('28% match')
  })

  it('labels overview retrieval without presenting a false zero score', () => {
    expect(
      sourceMatchLabel(source({ retrieval_method: 'overview', similarity: null })),
    ).toBe('Overview passage')
  })
})
