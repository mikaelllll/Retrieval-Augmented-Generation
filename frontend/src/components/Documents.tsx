import { FileText, LoaderCircle, Trash2, UploadCloud } from 'lucide-react'
import { useRef, useState } from 'react'
import type { DocumentRecord } from '../types'
import { Tooltip } from './Tooltip'

interface Props { documents: DocumentRecord[]; upload: (file: File) => Promise<void>; remove: (id: string) => Promise<void>; busy: boolean }

export function Documents({ documents, upload, remove, busy }: Props) {
  const input = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)
  const choose = (files: FileList | null) => files?.[0] && upload(files[0])

  return (
    <section className="card documents-card">
      <div className="section-heading">
        <span className="icon-box"><FileText size={19} /></span>
        <div><h2>Knowledge base</h2><p>Upload PDFs, then follow extraction and embedding progress.</p></div>
        <Tooltip text="A background worker extracts text, splits it into overlapping chunks, creates local embeddings, and stores them in pgvector." />
      </div>
      <button
        className={`dropzone ${dragging ? 'dropzone--active' : ''}`}
        onClick={() => input.current?.click()}
        onDragOver={(event) => { event.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={(event) => { event.preventDefault(); setDragging(false); choose(event.dataTransfer.files) }}
      >
        <UploadCloud size={28} /><strong>Drop a PDF here or browse</strong><span>PDF only · maximum 15 MB</span>
      </button>
      <input ref={input} hidden type="file" accept="application/pdf,.pdf" onChange={(event) => choose(event.target.files)} />
      <div className="document-list">
        {documents.length === 0 && <div className="empty-state">No documents yet. Upload one to inspect the pipeline.</div>}
        {documents.map((document) => (
          <article className="document" key={document.id}>
            <span className="document__glyph"><FileText size={20} /></span>
            <div className="document__body">
              <strong title={document.filename}>{document.filename}</strong>
              <span>{(document.size_bytes / 1024).toFixed(1)} KB · {document.page_count ?? '—'} pages · {document.chunk_count} chunks</span>
              {document.error_message && <span className="error-text">{document.error_message}</span>}
            </div>
            <span className={`status status--${document.status}`}>
              {(document.status === 'queued' || document.status === 'processing') && <LoaderCircle size={13} className="spin" />}
              {document.status}
            </span>
            <button className="icon-button danger" disabled={busy} onClick={() => remove(document.id)} aria-label={`Delete ${document.filename}`}><Trash2 size={17} /></button>
          </article>
        ))}
      </div>
    </section>
  )
}

