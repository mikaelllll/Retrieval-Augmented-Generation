import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Activity, Boxes, Database, Github, Network, ServerCog } from 'lucide-react'
import { useEffect, useState } from 'react'
import { api } from './api'
import { Chat } from './components/Chat'
import { Documents } from './components/Documents'
import { KeyPanel } from './components/KeyPanel'

export default function App() {
  const client = useQueryClient()
  const [apiKey, setApiKey] = useState('')
  const [verified, setVerified] = useState(false)
  const [notice, setNotice] = useState('')
  const documents = useQuery({
    queryKey: ['documents'],
    queryFn: api.documents,
    refetchInterval: (query) => query.state.data?.some((item) => ['queued', 'processing'].includes(item.status)) ? 2000 : false,
  })
  const upload = useMutation({ mutationFn: api.upload, onSuccess: () => { setNotice('Upload accepted. A background worker is processing the PDF.'); client.invalidateQueries({ queryKey: ['documents'] }) }, onError: (error) => setNotice(error.message) })
  const remove = useMutation({ mutationFn: api.remove, onSuccess: () => { setNotice('Document and its vectors were removed.'); client.invalidateQueries({ queryKey: ['documents'] }) }, onError: (error) => setNotice(error.message) })
  const ask = useMutation({ mutationFn: ({ question, ids }: { question: string; ids: string[] }) => api.ask(question, ids, apiKey) })

  useEffect(() => {
    if (!notice) return
    const timer = window.setTimeout(() => setNotice(''), 5000)
    return () => window.clearTimeout(timer)
  }, [notice])

  const records = documents.data ?? []
  const ready = records.filter((item) => item.status === 'ready').length
  const chunks = records.reduce((sum, item) => sum + item.chunk_count, 0)

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top"><span className="brand__mark"><Network size={22} /></span><span>RAG<span>Explorer</span></span></a>
        <nav><a href="#workspace">Workspace</a><a href="#architecture">Architecture</a><a href="/docs" target="_blank" rel="noreferrer">API</a></nav>
        <a className="github-link" href="https://github.com/mikaelllll/Retrieval-Augmented-Generation" target="_blank" rel="noreferrer"><Github size={18} /> GitHub</a>
      </header>

      <main id="top">
        <section className="hero">
          <div className="hero__eyebrow"><Activity size={14} /> Production-minded RAG, made inspectable</div>
          <h1>Ask your documents.<br /><span>See how every answer was built.</span></h1>
          <p>Upload PDFs, generate embeddings locally, retrieve evidence with PostgreSQL and pgvector, then produce cited answers with Gemini.</p>
          <div className="pipeline" id="architecture">
            {[
              ['01', 'Extract', 'PDF text + pages'], ['02', 'Embed', 'Local MiniLM model'], ['03', 'Retrieve', 'pgvector similarity'], ['04', 'Generate', 'Gemini + citations'],
            ].map(([number, title, text], index) => <div className="pipeline__step" key={title}><span>{number}</span><div><strong>{title}</strong><small>{text}</small></div>{index < 3 && <i>→</i>}</div>)}
          </div>
        </section>

        <section className="stats" aria-label="Workspace status">
          <div><span className="stat-icon"><Database size={20} /></span><p><strong>{ready}</strong><small>Ready documents</small></p></div>
          <div><span className="stat-icon"><Boxes size={20} /></span><p><strong>{chunks}</strong><small>Embedded chunks</small></p></div>
          <div><span className="stat-icon"><ServerCog size={20} /></span><p><strong>{verified ? 'Online' : 'Waiting'}</strong><small>Gemini provider</small></p></div>
        </section>

        <div id="workspace" className="workspace">
          <KeyPanel apiKey={apiKey} setApiKey={setApiKey} verified={verified} setVerified={setVerified} />
          {notice && <div className="toast" role="status">{notice}</div>}
          <div className="workspace-grid">
            <Documents documents={records} upload={async (file) => { await upload.mutateAsync(file) }} remove={async (id) => { await remove.mutateAsync(id) }} busy={upload.isPending || remove.isPending} />
            <Chat documents={records} verified={verified} asking={ask.isPending} onAsk={(question, ids) => ask.mutateAsync({ question, ids })} />
          </div>
        </div>
      </main>
      <footer><span>RAG Explorer · portfolio engineering project</span><span>FastAPI · React · PostgreSQL · Redis · Celery · Gemini</span></footer>
    </div>
  )
}

