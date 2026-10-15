import { useState } from 'react'
import { ArrowUpRight, LockKeyhole, Menu, Scale, X } from 'lucide-react'

const NAV_ITEMS = [['/', 'Home'], ['/analyzer', 'Analyzer'], ['/how-it-works', 'How it works'], ['/solutions', 'Solutions'], ['/security', 'Security']]

export function AppLink({ to, navigate, className = '', children, onClick }) {
  return <a href={to} className={className} onClick={(event) => { if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return; event.preventDefault(); onClick?.(); navigate(to) }}>{children}</a>
}

export default function SiteLayout({ pathname, navigate, children }) {
  const [menuOpen, setMenuOpen] = useState(false)
  return (
    <div className="site-shell">
      <header className="site-header">
        <div className="header-inner">
          <AppLink to="/" navigate={navigate} className="site-brand" onClick={() => setMenuOpen(false)}>
            <span className="brand-sun"><Scale size={21} /></span>
            <span className="brand-word">LEGAL<span>EASE</span><small>AI CONTRACT INTELLIGENCE</small></span>
          </AppLink>
          <nav className={`site-nav ${menuOpen ? 'open' : ''}`} aria-label="Main navigation">
            {NAV_ITEMS.map(([path, label]) => <AppLink key={path} to={path} navigate={navigate} onClick={() => setMenuOpen(false)} className={pathname === path ? 'active' : ''}>{label}</AppLink>)}
            <AppLink to="/analyzer" navigate={navigate} onClick={() => setMenuOpen(false)} className="nav-cta mobile-only">Analyze now <ArrowUpRight size={17} /></AppLink>
            <AppLink to="/admin/login" navigate={navigate} onClick={() => setMenuOpen(false)} className="admin-link mobile-only"><LockKeyhole size={15} /> Admin login</AppLink>
          </nav>
          <div className="header-actions"><AppLink to="/admin/login" navigate={navigate} className="admin-link desktop-cta"><LockKeyhole size={15} /> Admin</AppLink><AppLink to="/analyzer" navigate={navigate} className="nav-cta desktop-cta">Analyze now <ArrowUpRight size={17} /></AppLink></div>
          <button className="menu-toggle" onClick={() => setMenuOpen(!menuOpen)} aria-expanded={menuOpen} aria-label="Toggle navigation">{menuOpen ? <X /> : <Menu />}</button>
        </div>
      </header>
      {children}
      {!pathname.startsWith('/admin') && <footer className="site-footer">
        <div className="footer-top">
          <div className="footer-brand-block"><div className="site-brand inverted"><span className="brand-sun"><Scale size={21} /></span><span className="brand-word">LEGAL<span>EASE</span><small>AI CONTRACT INTELLIGENCE</small></span></div><p>Agentic AI that turns dense contract language into clear risk findings and practical next steps.</p></div>
          <div className="footer-links"><div><strong>Product</strong><AppLink to="/analyzer" navigate={navigate}>Contract analyzer</AppLink><AppLink to="/how-it-works" navigate={navigate}>Agent workflow</AppLink><AppLink to="/solutions" navigate={navigate}>Contract types</AppLink></div><div><strong>Trust</strong><AppLink to="/security" navigate={navigate}>Security</AppLink><span>Private local mode</span><span>Responsible AI</span></div></div>
        </div>
        <div className="footer-bottom"><span>© 2026 LegalEase. Built for informed contract review.</span><span>Informational analysis, not legal advice.</span></div>
      </footer>}
    </div>
  )
}
