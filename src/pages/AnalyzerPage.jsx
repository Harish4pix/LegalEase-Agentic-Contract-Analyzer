import { useEffect, useMemo, useRef, useState } from 'react'
import { AlertCircle, ArrowLeft, Bot, Check, ChevronDown, Clock3, Download, FileCheck2, FileText, LockKeyhole, MessageSquareText, Search, ShieldCheck, Sparkles, UploadCloud, WandSparkles } from 'lucide-react'
import ChatPanel from '../components/ChatPanel.jsx'
import RiskGauge from '../components/RiskGauge.jsx'

const SAMPLE_CONTRACT = `SERVICE AGREEMENT

1. SERVICES
The Provider will provide advisory and technical services requested by the Client.

2. PAYMENT
Invoices are payable within 10 days. A late fee of 5% per week will apply to unpaid amounts.

3. LIABILITY
The Client accepts unlimited liability for any loss, whether direct, indirect, incidental, or consequential, arising from this Agreement.

4. INDEMNITY
The Client shall indemnify and hold harmless the Provider from every claim, cost, loss, and expense of any kind, including claims caused by the Provider's negligence.

5. TERM AND TERMINATION
The Provider may terminate immediately without notice in its sole discretion. The Agreement will automatically renew for successive one-year terms unless the Client gives 120 days' notice.

6. CONFIDENTIALITY
Each party must protect the other party's confidential information and use it only to perform this Agreement.

7. INTELLECTUAL PROPERTY
The Client grants the Provider a perpetual, irrevocable, worldwide licence to use all materials created under this Agreement.

8. DISPUTES
The courts of Maharashtra will have exclusive jurisdiction over disputes arising from this Agreement.`

const STEPS = ['Reading and validating the document', 'Separating clauses and obligations', 'Assessing legal and commercial risks', 'Calibrating scores and recommendations', 'Compiling your analysis report']
const levelLabel = (level) => `${level.charAt(0).toUpperCase()}${level.slice(1)} risk`

export default function AnalyzerPage() {
  const inputRef = useRef(null)
  const [phase, setPhase] = useState('upload')
  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [analysis, setAnalysis] = useState(null)
  const [config, setConfig] = useState(null)
  const [error, setError] = useState('')
  const [elapsed, setElapsed] = useState(0)
  const [filter, setFilter] = useState('all')
  const [search, setSearch] = useState('')
  const [expanded, setExpanded] = useState(new Set())
  const [chatOpen, setChatOpen] = useState(false)

  useEffect(() => { fetch('/api/config').then((res) => res.json()).then(setConfig).catch(() => setConfig(null)) }, [])
  useEffect(() => {
    if (phase !== 'analyzing') return undefined
    const started = Date.now()
    const timer = window.setInterval(() => setElapsed(Math.floor((Date.now() - started) / 1000)), 1000)
    return () => window.clearInterval(timer)
  }, [phase])

  const visibleRisks = useMemo(() => analysis?.risky_clauses.filter((risk) => {
    const matchesLevel = filter === 'all' || risk.risk_level === filter
    return matchesLevel && `${risk.title} ${risk.clause_text} ${risk.risk_factors.join(' ')}`.toLowerCase().includes(search.toLowerCase())
  }) || [], [analysis, filter, search])

  function chooseFile(selected) {
    setError('')
    if (!selected) return
    const extension = selected.name.split('.').pop().toLowerCase()
    if (!['pdf', 'docx', 'txt'].includes(extension)) return setError('Please choose a PDF, DOCX, or TXT contract.')
    if (selected.size > (config?.max_upload_mb || 10) * 1024 * 1024) return setError(`The maximum file size is ${config?.max_upload_mb || 10} MB.`)
    setFile(selected)
  }

  async function analyze() {
    if (!file) return
    setPhase('analyzing'); setElapsed(0); setError('')
    const form = new FormData(); form.append('file', file)
    try {
      const response = await fetch('/api/analyze', { method: 'POST', body: form })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'The contract could not be analyzed.')
      setAnalysis(data); setExpanded(new Set(data.risky_clauses.slice(0, 2).map((risk) => risk.id))); setPhase('results')
    } catch (requestError) { setError(requestError.message); setPhase('upload') }
  }

  function reset() { setPhase('upload'); setFile(null); setAnalysis(null); setError(''); setFilter('all'); setSearch('') }
  function toggleRisk(id) { setExpanded((current) => { const next = new Set(current); next.has(id) ? next.delete(id) : next.add(id); return next }) }

  if (phase === 'analyzing') return (
    <main className="analysis-progress-page analyzer-surface"><section className="analysis-progress-card"><div className="analysis-visual"><span className="analysis-chip chip-left"><FileCheck2 size={15} /> Extracting</span><span className="analysis-chip chip-right"><ShieldCheck size={15} /> Reviewing</span><span className="analysis-chip chip-bottom"><Bot size={15} /> Coordinating</span><div className="document-orbit"><span className="orbit orbit-one" /><span className="orbit orbit-two" /><FileText size={35} /></div></div><span className="step-label">AGENT PIPELINE ACTIVE</span><h1>Reviewing {file?.name}</h1><p>Each specialist agent is completing one focused part of the review.</p><div className="analysis-progress-track"><span style={{ width: `${Math.min(92, 16 + elapsed * 4)}%` }} /></div><div className="agent-steps">{STEPS.map((step, index) => { const active = Math.min(4, Math.floor(elapsed / 3)); return <div className={`${index < active ? 'done' : ''} ${index === active ? 'active' : ''}`} key={step}><span>{index < active ? <Check size={16} /> : index + 1}</span><p>{step}</p>{index === active && <small>In progress</small>}</div> })}</div><div className="elapsed"><Clock3 size={16} /> {elapsed}s elapsed</div></section>
  </main>)

  if (phase === 'results' && analysis) return (
    <main className="results-page analyzer-surface"><div className="results-toolbar"><button className="back-button" onClick={reset}><ArrowLeft size={18} /> New analysis</button><div className="document-name"><FileText size={18} /><span><strong>{analysis.filename}</strong><small>{analysis.contract_type}</small></span></div><div className="toolbar-actions"><span className="complete-chip"><Check size={15} /> Analyzed in {analysis.processing_seconds}s</span><button className="assistant-button" onClick={() => setChatOpen(true)}><MessageSquareText size={17} /> Ask assistant</button><a className="report-button" href={`/api/analyses/${analysis.contract_id}/report`}><Download size={17} /> Download report</a></div></div>
      <div className="results-layout"><section className="results-content"><div className="results-overview-label"><span className="section-tag">ANALYSIS OVERVIEW</span><p>Review the highest-priority clauses first, then open any finding for supporting text and recommendations.</p></div><div className="summary-grid"><article className={`overall-card ${analysis.overall_risk_level}`}><div><span>OVERALL CONTRACT RISK</span><h2>{levelLabel(analysis.overall_risk_level)}</h2><p>{analysis.summary}</p></div><RiskGauge score={analysis.overall_risk_score} level={analysis.overall_risk_level} /></article>{['high', 'medium', 'low'].map((level) => <button className={`stat-card ${level} ${filter === level ? 'selected' : ''}`} key={level} onClick={() => setFilter(filter === level ? 'all' : level)}><span className="stat-dot" /><div><strong>{analysis.risk_distribution[level]}</strong><span>{levelLabel(level)}</span></div><small>View findings</small></button>)}</div>
        <div className="findings-header"><div><span className="step-label">CLAUSE REVIEW</span><h2>Risk findings</h2><p>{analysis.clauses_reviewed} clauses reviewed · {analysis.risky_clauses.length} flagged</p></div><div className="finding-tools"><label className="search-box"><Search size={17} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search findings" /></label><select value={filter} onChange={(event) => setFilter(event.target.value)} aria-label="Filter risk level"><option value="all">All risks</option><option value="high">High risk</option><option value="medium">Medium risk</option><option value="low">Low risk</option></select></div></div>
        <div className="risk-list">{visibleRisks.length === 0 && <div className="empty-state"><ShieldCheck size={26} /><h3>No matching findings</h3><p>Try another risk level or search term.</p></div>}{visibleRisks.map((risk, index) => { const isOpen = expanded.has(risk.id); return <article className={`risk-card ${risk.risk_level}`} key={risk.id}><button className="risk-card-summary" onClick={() => toggleRisk(risk.id)} aria-expanded={isOpen}><span className="finding-number">{String(index + 1).padStart(2, '0')}</span><span className="risk-card-title"><strong>{risk.title}</strong><small>{risk.risk_factors.join(' · ')}</small></span><span className={`risk-badge ${risk.risk_level}`}>{risk.risk_level}</span><span className="score-pill"><strong>{risk.risk_score}</strong>/100</span><ChevronDown className={isOpen ? 'rotated' : ''} size={20} /></button>{isOpen && <div className="risk-card-body"><div className="risk-explanation"><h3>Why this matters</h3><p>{risk.explanation}</p></div><div className="recommendation"><h3><Sparkles size={16} /> Recommended action</h3><p>{risk.recommendation}</p></div><details><summary>View original clause text</summary><blockquote>{risk.clause_text}</blockquote></details><div className="confidence">AI confidence <span><i style={{ width: `${risk.confidence}%` }} /></span> {risk.confidence}%</div></div>}</article> })}</div>
        <div className="legal-notice"><AlertCircle size={18} /><p><strong>Informational review only.</strong> {analysis.disclaimer}</p></div></section></div>
      <button className="assistant-fab" onClick={() => setChatOpen(true)}><MessageSquareText size={21} /><span>Ask LegalEase</span></button>
      {chatOpen && (
        <aside className="chat-widget" role="dialog" aria-label="LegalEase contract assistant">
          <ChatPanel
            contractId={analysis.contract_id}
            filename={analysis.filename}
            onClose={() => setChatOpen(false)}
          />
        </aside>
      )}
    </main>)

  return (
    <main className="analyzer-landing"><section className="analyzer-title"><span className="section-tag">CONTRACT ANALYZER</span><h1>Upload once. Understand every risk.</h1><p>Your document moves through a coordinated agent pipeline and returns as a structured, clause-level review.</p><div className="analyzer-trust"><span><Clock3 /> Typically under 30 seconds</span><span><LockKeyhole /> Originals are not stored</span><span><FileCheck2 /> PDF report included</span></div></section>
      <section className="upload-workspace"><div className="workspace-head"><div><span className="step-label">NEW ANALYSIS</span><h2>Choose your contract</h2><p>The clearest results come from searchable text documents.</p></div><div className="provider-status"><span className={`provider-dot ${config?.provider === 'demo' ? 'demo' : ''}`} /><small>ANALYSIS MODE</small><b>{config ? (config.provider === 'demo' ? 'Demo rules' : config.model) : 'Connecting…'}</b></div></div>
        <div className={`dropzone ${dragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`} onDragOver={(event) => { event.preventDefault(); setDragging(true) }} onDragLeave={() => setDragging(false)} onDrop={(event) => { event.preventDefault(); setDragging(false); chooseFile(event.dataTransfer.files[0]) }}><input ref={inputRef} type="file" accept=".pdf,.docx,.txt" onChange={(event) => chooseFile(event.target.files[0])} />{file ? <><span className="upload-icon success"><FileText size={30} /></span><strong>{file.name}</strong><p>{(file.size / 1024).toFixed(1)} KB · Ready for review</p><button className="text-button" onClick={() => inputRef.current?.click()}>Choose another file</button></> : <><span className="upload-icon"><UploadCloud size={30} /></span><strong>Drag and drop your contract</strong><p>or browse from your computer</p><button className="secondary-button" onClick={() => inputRef.current?.click()}>Select a document</button><small>PDF, DOCX, or TXT · Up to {config?.max_upload_mb || 10} MB</small></>}</div>
        {error && <div className="inline-error"><AlertCircle size={17} /> {error}</div>}<div className="workspace-actions"><button className="sample-button" onClick={() => chooseFile(new File([SAMPLE_CONTRACT], 'sample-service-agreement.txt', { type: 'text/plain' }))}>Load a sample agreement</button><button className="primary-button" onClick={analyze} disabled={!file}><WandSparkles size={18} /> Run agent analysis</button></div>{config?.provider === 'demo' && <p className="mode-notice"><AlertCircle size={15} /> Demo mode uses keyword rules. Add a free Gemini API key for complete AI analysis.</p>}
      </section>
      <aside className="analyzer-side-note"><ShieldCheck size={22} /><div><b>Designed for responsible review</b><p>LegalEase surfaces issues and negotiating points. It does not replace advice from a qualified lawyer.</p></div></aside>
    </main>)
}
