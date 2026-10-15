import { useEffect, useMemo, useState } from 'react'
import { Activity, AlertTriangle, BarChart3, Bell, BriefcaseBusiness, CheckCircle2, ChevronRight, CircleGauge, Clock3, Download, FileText, LayoutDashboard, LogOut, Plus, Search, ShieldCheck, Users } from 'lucide-react'

const TABS = [['overview', LayoutDashboard, 'Overview'], ['contracts', FileText, 'Contracts'], ['clients', BriefcaseBusiness, 'Clients'], ['team', Users, 'Team'], ['analytics', BarChart3, 'Analytics'], ['audit', Activity, 'Audit log']]
const labels = { pending: 'Pending', under_review: 'Under review', approved: 'Approved', rejected: 'Rejected', archived: 'Archived' }

export default function AdminDashboardPage({ navigate }) {
  const [tab, setTab] = useState('overview')
  const [dashboard, setDashboard] = useState(null)
  const [contracts, setContracts] = useState([])
  const [clients, setClients] = useState([])
  const [team, setTeam] = useState([])
  const [audit, setAudit] = useState([])
  const [search, setSearch] = useState('')
  const [error, setError] = useState('')
  const token = sessionStorage.getItem('legalease_admin_token')

  async function request(path, options = {}) {
    const response = await fetch(path, { ...options, headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}`, ...options.headers } })
    if (response.status === 401) { sessionStorage.removeItem('legalease_admin_token'); navigate('/admin/login'); throw new Error('Your session expired.') }
    const data = await response.json(); if (!response.ok) throw new Error(data.detail || 'Request failed.'); return data
  }
  async function load() {
    try { const [d, c, cl, t, a] = await Promise.all(['/api/admin/dashboard','/api/admin/contracts','/api/admin/clients','/api/admin/team','/api/admin/audit'].map((path) => request(path))); setDashboard(d); setContracts(c); setClients(cl); setTeam(t); setAudit(a) } catch (e) { setError(e.message) }
  }
  useEffect(() => {
    const timer = window.setTimeout(() => { if (!token) navigate('/admin/login'); else load() }, 0)
    return () => window.clearTimeout(timer)
    // The initial session check intentionally runs once for this route.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function updateContract(id, changes) { await request(`/api/admin/contracts/${id}`, { method: 'PATCH', body: JSON.stringify(changes) }); await load() }
  async function add(kind) {
    const name = window.prompt(`Enter ${kind === 'clients' ? 'client/company' : 'team member'} name:`); if (!name) return
    const email = window.prompt('Email address (optional):') || ''
    await request(`/api/admin/${kind}`, { method: 'POST', body: JSON.stringify({ name, email, role: kind === 'team' ? 'Legal Reviewer' : 'Client' }) }); await load()
  }
  function logout() { sessionStorage.removeItem('legalease_admin_token'); navigate('/admin/login') }
  const filtered = useMemo(() => contracts.filter((c) => `${c.filename} ${c.client} ${c.reviewer}`.toLowerCase().includes(search.toLowerCase())), [contracts, search])
  if (!dashboard) return <main className="admin-loading"><CircleGauge /><h2>Loading legal operations workspace</h2>{error && <p>{error}</p>}</main>

  return <main className="admin-shell"><aside className="admin-sidebar"><div className="admin-firm"><span>LE</span><div><strong>LegalEase</strong><small>LEGAL OPERATIONS</small></div></div><nav>{TABS.map(([id, Icon, label]) => <button key={id} className={tab === id ? 'active' : ''} onClick={() => setTab(id)}><Icon size={18} />{label}{id === 'contracts' && <small>{contracts.length}</small>}</button>)}</nav><div className="admin-sidebar-foot"><div><span className="admin-avatar">A</span><p><strong>Firm Admin</strong><small>{sessionStorage.getItem('legalease_admin_email')}</small></p></div><button onClick={logout} aria-label="Log out"><LogOut size={18} /></button></div></aside><section className="admin-main"><header className="admin-topbar"><div><span className="step-label">FIRM ADMINISTRATION</span><h1>{TABS.find(([id]) => id === tab)?.[2]}</h1></div><div><button className="notification-button"><Bell size={18} />{dashboard.alerts.length > 0 && <span>{dashboard.alerts.length}</span>}</button><button className="admin-primary" onClick={() => navigate('/analyzer')}>Analyze contract <ChevronRight size={17} /></button></div></header>{error && <div className="admin-error">{error}</div>}
    {tab === 'overview' && <><div className="admin-metrics"><Metric icon={FileText} label="Total contracts" value={dashboard.total} note="All analyzed records"/><Metric icon={AlertTriangle} label="High risk" value={dashboard.risks.high} note="Requires priority review" tone="danger"/><Metric icon={Clock3} label="Pending review" value={dashboard.status.pending + dashboard.status.under_review} note="Awaiting legal action" tone="warning"/><Metric icon={CheckCircle2} label="Approved" value={dashboard.status.approved} note="Completed reviews" tone="success"/></div><div className="admin-grid"><section className="admin-panel wide"><PanelHead title="Recent contracts" action={() => setTab('contracts')} actionLabel="View all"/><ContractTable contracts={dashboard.recent} onUpdate={updateContract} compact /></section><section className="admin-panel"><PanelHead title="Risk portfolio"/><RiskBars risks={dashboard.risks} total={dashboard.total}/><div className="average-risk"><CircleGauge /><span><small>AVERAGE RISK SCORE</small><strong>{dashboard.average_risk}/100</strong></span></div></section><section className="admin-panel"><PanelHead title="Review progress"/><StatusList status={dashboard.status}/></section><section className="admin-panel wide"><PanelHead title="Renewal & expiry alerts"/><Alerts alerts={dashboard.alerts}/></section></div></>}
    {tab === 'contracts' && <section className="admin-panel full"><div className="contract-controls"><PanelHead title="Contract register"/><label><Search size={17}/><input placeholder="Search contracts, clients or reviewers" value={search} onChange={(e) => setSearch(e.target.value)}/></label></div><ContractTable contracts={filtered} onUpdate={updateContract}/></section>}
    {(tab === 'clients' || tab === 'team') && <section className="admin-panel full"><PanelHead title={tab === 'clients' ? 'Client directory' : 'Legal team'} action={() => add(tab)} actionLabel={tab === 'clients' ? 'Add client' : 'Add member'} icon={Plus}/><Directory items={tab === 'clients' ? clients : team} empty={tab === 'clients' ? 'No clients added yet.' : 'No team members added yet.'}/></section>}
    {tab === 'analytics' && <div className="admin-grid"><section className="admin-panel"><PanelHead title="Risk distribution"/><RiskBars risks={dashboard.risks} total={dashboard.total}/></section><section className="admin-panel"><PanelHead title="Review status"/><StatusList status={dashboard.status}/></section><section className="admin-panel wide analytics-callout"><BarChart3/><div><span className="step-label">PORTFOLIO INSIGHT</span><h2>{dashboard.risks.high ? `${dashboard.risks.high} high-risk contract${dashboard.risks.high === 1 ? '' : 's'} need attention.` : 'No high-risk contracts currently require attention.'}</h2><p>The portfolio average is {dashboard.average_risk}/100 across {dashboard.total} analyzed contracts.</p></div></section></div>}
    {tab === 'audit' && <section className="admin-panel full"><PanelHead title="Activity and audit history"/><div className="audit-list">{audit.length ? audit.map((item, index) => <article key={`${item.timestamp}-${index}`}><span><ShieldCheck size={16}/></span><div><strong>{item.action}</strong><p>{item.actor}</p></div><time>{new Date(item.timestamp).toLocaleString()}</time></article>) : <Empty text="No administrative activity recorded yet."/>}</div></section>}
  </section></main>
}

function Metric({ icon: Icon, label, value, note, tone='' }) { return <article className={`admin-metric ${tone}`}><span><Icon /></span><div><small>{label}</small><strong>{value}</strong><p>{note}</p></div></article> }
function PanelHead({ title, action, actionLabel, icon: Icon }) { return <div className="panel-head"><h2>{title}</h2>{action && <button onClick={action}>{Icon && <Icon size={15}/>} {actionLabel}</button>}</div> }
function ContractTable({ contracts, onUpdate, compact=false }) { return <div className="contract-table-wrap">{contracts.length ? <table className="contract-table"><thead><tr><th>Contract</th><th>Risk</th>{!compact && <th>Client</th>}<th>Reviewer</th><th>Status</th><th>Report</th></tr></thead><tbody>{contracts.map((c) => <tr key={c.contract_id}><td><strong>{c.filename}</strong><small>{c.contract_type} · {new Date(c.created_at).toLocaleDateString()}</small></td><td><span className={`table-risk ${c.risk_level}`}>{c.risk_score}</span></td>{!compact && <td><input value={c.client === 'Unassigned' ? '' : c.client} placeholder="Assign client" onChange={(e) => onUpdate(c.contract_id,{client:e.target.value})}/></td>}<td><input value={c.reviewer === 'Unassigned' ? '' : c.reviewer} placeholder="Assign reviewer" onChange={(e) => onUpdate(c.contract_id,{reviewer:e.target.value})}/></td><td><select value={c.status} onChange={(e) => onUpdate(c.contract_id,{status:e.target.value})}>{Object.entries(labels).map(([v,l]) => <option value={v} key={v}>{l}</option>)}</select></td><td><a href={`/api/analyses/${c.contract_id}/report`} aria-label="Download report"><Download size={17}/></a></td></tr>)}</tbody></table> : <Empty text="Analyze a contract to create the first firm record."/>}</div> }
function RiskBars({ risks, total }) { return <div className="risk-bars">{['high','medium','low'].map((level) => <div key={level}><p><span>{level} risk</span><strong>{risks[level]}</strong></p><i><span className={level} style={{width:`${total ? Math.max(5,risks[level]/total*100) : 0}%`}}/></i></div>)}</div> }
function StatusList({ status }) { const total=Object.values(status).reduce((a,b)=>a+b,0); return <div className="status-list">{Object.entries(status).filter(([k])=>k!=='archived').map(([key,value]) => <div key={key}><span className={`status-dot ${key}`}/><p>{labels[key]}<small>{total ? Math.round(value/total*100) : 0}% of portfolio</small></p><strong>{value}</strong></div>)}</div> }
function Alerts({ alerts }) { return alerts.length ? <div className="alert-list">{alerts.map(a=><article key={a.contract_id}><Bell/><div><strong>{a.filename}</strong><p>Renewal or expiry date: {a.expiry_date}</p></div><span>{a.reviewer}</span></article>)}</div> : <Empty text="No upcoming renewal or expiry dates. Add dates from contract tracking to receive alerts."/> }
function Directory({ items, empty }) { return items.length ? <div className="directory-grid">{items.map(item=><article key={item.id}><span>{item.name.charAt(0).toUpperCase()}</span><div><strong>{item.name}</strong><p>{item.email || 'No email provided'}</p><small>{item.role}</small></div></article>)}</div> : <Empty text={empty}/> }
function Empty({ text }) { return <div className="admin-empty"><ShieldCheck/><h3>Nothing to show yet</h3><p>{text}</p></div> }
