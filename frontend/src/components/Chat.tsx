import { Bot, CornerDownLeft, Search, Sparkles } from 'lucide-react'
import { FormEvent, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import type { Answer, DocumentRecord } from '../types'
import { Tooltip } from './Tooltip'

interface Props { documents: DocumentRecord[]; verified: boolean; asking: boolean; onAsk: (question: string, ids: string[]) => Promise<Answer> }

export function Chat({ documents, verified, asking, onAsk }: Props) {
  const [question, setQuestion] = useState('')
  const [selected, setSelected] = useState<string[]>([])
  const [answer, setAnswer] = useState<Answer | null>(null)
  const [error, setError] = useState('')
  const ready = documents.filter((document) => document.status === 'ready')

  async function submit(event: FormEvent) {
    event.preventDefault(); setError(''); setAnswer(null)
    try { setAnswer(await onAsk(question, selected)); setQuestion('') }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Question failed') }
  }

  return (
    <section className="card chat-card">
      <div className="section-heading">
        <span className="icon-box icon-box--violet"><Sparkles size={19} /></span>
        <div><h2>Ask with evidence</h2><p>Inspect retrieval scores, sources, and model latency.</p></div>
        <Tooltip text="Your question is embedded locally. pgvector selects relevant passages; only those passages are sent to Gemini to compose the answer." />
      </div>
      <div className="filters">
        <span>Scope:</span>
        <button className={selected.length === 0 ? 'chip chip--active' : 'chip'} onClick={() => setSelected([])}>All ready documents</button>
        {ready.map((document) => (
          <button key={document.id} className={selected.includes(document.id) ? 'chip chip--active' : 'chip'} onClick={() => setSelected((old) => old.includes(document.id) ? old.filter((id) => id !== document.id) : [...old, document.id])}>{document.filename}</button>
        ))}
      </div>
      <form className="question-box" onSubmit={submit}>
        <Search size={20} />
        <textarea value={question} maxLength={2000} placeholder="Ask a question about your documents…" onChange={(event) => setQuestion(event.target.value)} />
        <button className="send-button" disabled={!verified || ready.length === 0 || question.trim().length < 3 || asking} aria-label="Ask question"><CornerDownLeft size={19} /></button>
      </form>
      {!verified && <div className="inline-hint">Connect Gemini above to generate an answer.</div>}
      {ready.length === 0 && <div className="inline-hint">At least one document must finish processing.</div>}
      {error && <div className="alert alert--error">{error}</div>}
      {asking && <div className="answer-loading"><Bot size={22} /><span>Retrieving evidence and asking Gemini…</span></div>}
      {answer && (
        <div className="answer">
          <div className="answer__header"><Bot size={21} /><strong>{answer.status === 'answered' ? 'Grounded answer' : 'Insufficient evidence'}</strong><span>{answer.model}</span></div>
          <div className="answer__text"><ReactMarkdown>{answer.answer}</ReactMarkdown></div>
          <div className="metrics"><span>Retrieval <strong>{answer.retrieval_ms} ms</strong></span><span>Generation <strong>{answer.generation_ms} ms</strong></span><span>Sources <strong>{answer.sources.length}</strong></span></div>
          {answer.sources.length > 0 && <div className="sources"><h3>Retrieved evidence</h3>{answer.sources.map((source) => <details key={`${source.document_id}-${source.citation}`}><summary><strong>{source.citation}</strong> {source.filename} · page {source.page_number}<span>{Math.round(source.similarity * 100)}% match</span></summary><p>{source.content}</p></details>)}</div>}
        </div>
      )}
    </section>
  )
}

