import { Eye, EyeOff, KeyRound, ShieldCheck } from 'lucide-react'
import { useState } from 'react'
import { api } from '../api'
import { Tooltip } from './Tooltip'

interface Props { apiKey: string; setApiKey: (value: string) => void; verified: boolean; setVerified: (value: boolean) => void }

export function KeyPanel({ apiKey, setApiKey, verified, setVerified }: Props) {
  const [visible, setVisible] = useState(false)
  const [checking, setChecking] = useState(false)
  const [message, setMessage] = useState('')

  async function verify() {
    setChecking(true); setMessage('')
    try {
      const result = await api.checkKey(apiKey)
      setVerified(true); setMessage(`${result.message} · ${result.model}`)
    } catch (error) {
      setVerified(false); setMessage(error instanceof Error ? error.message : 'Verification failed')
    } finally { setChecking(false) }
  }

  return (
    <section className="card key-panel">
      <div className="section-heading">
        <span className="icon-box"><KeyRound size={19} /></span>
        <div><h2>Connect Gemini</h2><p>Bring your own free API key to generate grounded answers.</p></div>
        <Tooltip text="The key is kept only in this page's memory. It is sent directly to the backend per request and is not persisted or logged." />
      </div>
      <div className="key-row">
        <div className="input-with-action">
          <input
            aria-label="Gemini API key"
            type={visible ? 'text' : 'password'}
            value={apiKey}
            autoComplete="off"
            placeholder="Paste your Gemini API key"
            onChange={(event) => { setApiKey(event.target.value); setVerified(false); setMessage('') }}
          />
          <button className="icon-button" onClick={() => setVisible(!visible)} aria-label={visible ? 'Hide key' : 'Show key'}>
            {visible ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        </div>
        <button className="button button--primary" disabled={checking || apiKey.length < 20} onClick={verify}>
          {checking ? 'Checking…' : verified ? 'Connected' : 'Verify key'}
        </button>
      </div>
      <div className={`privacy-note ${verified ? 'privacy-note--success' : ''}`}>
        <ShieldCheck size={16} />
        <span>{message || 'Session-only: refreshing or closing this page removes the key.'}</span>
      </div>
    </section>
  )
}

