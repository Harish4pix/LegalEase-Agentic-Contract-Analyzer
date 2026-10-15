import { useEffect, useState } from 'react'
import { ArrowRight, LockKeyhole, Scale, ShieldCheck } from 'lucide-react'

export default function AdminLoginPage({ navigate }) {
  const [email, setEmail] = useState('admin@legalease.local')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => { if (sessionStorage.getItem('legalease_admin_token')) navigate('/admin') }, [navigate])

  async function login(event) {
    event.preventDefault(); setLoading(true); setError('')
    try {
      const response = await fetch('/api/admin/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Unable to sign in.')
      sessionStorage.setItem('legalease_admin_token', data.token)
      sessionStorage.setItem('legalease_admin_email', data.admin.email)
      navigate('/admin')
    } catch (requestError) { setError(requestError.message) } finally { setLoading(false) }
  }

  return <main className="admin-login-page"><section className="login-value"><span className="admin-eyebrow">LEGAL OPERATIONS WORKSPACE</span><h1>One view of every contract, risk and review.</h1><p>Securely manage the firm’s contract portfolio while the public analyzer continues to work independently.</p><div className="login-benefits"><span><ShieldCheck /> Protected firm workspace</span><span><Scale /> Human review over AI findings</span></div></section><section className="login-card"><div className="login-icon"><LockKeyhole /></div><span className="step-label">ADMIN ACCESS</span><h2>Sign in to your firm</h2><p>Use the administrator credentials configured on the server.</p><form onSubmit={login}><label>Email address<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label><label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Enter password" required /></label>{error && <div className="admin-error">{error}</div>}<button disabled={loading}>{loading ? 'Signing in…' : <>Secure sign in <ArrowRight size={17} /></>}</button></form><small>Authorized firm personnel only. Activity is recorded.</small></section></main>
}
