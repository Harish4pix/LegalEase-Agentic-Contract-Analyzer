import { useEffect, useState } from 'react'
import SiteLayout from './components/SiteLayout.jsx'
import AnalyzerPage from './pages/AnalyzerPage.jsx'
import HomePage from './pages/HomePage.jsx'
import HowItWorksPage from './pages/HowItWorksPage.jsx'
import SecurityPage from './pages/SecurityPage.jsx'
import SolutionsPage from './pages/SolutionsPage.jsx'
import AdminLoginPage from './pages/AdminLoginPage.jsx'
import AdminDashboardPage from './pages/AdminDashboardPage.jsx'

const ROUTES = {
  '/': HomePage,
  '/analyzer': AnalyzerPage,
  '/how-it-works': HowItWorksPage,
  '/solutions': SolutionsPage,
  '/security': SecurityPage,
  '/admin/login': AdminLoginPage,
  '/admin': AdminDashboardPage,
}

function usePathname() {
  const [pathname, setPathname] = useState(window.location.pathname)
  const [transitioning, setTransitioning] = useState(true)
  useEffect(() => {
    const initialTimer = window.setTimeout(() => setTransitioning(false), 650)
    const onPopState = () => {
      setTransitioning(true)
      setPathname(window.location.pathname)
      window.setTimeout(() => setTransitioning(false), 520)
    }
    window.addEventListener('popstate', onPopState)
    return () => { window.clearTimeout(initialTimer); window.removeEventListener('popstate', onPopState) }
  }, [])
  function navigate(path) {
    if (path === pathname) return
    setTransitioning(true)
    window.history.pushState({}, '', path)
    setPathname(path)
    window.scrollTo({ top: 0, behavior: 'smooth' })
    window.setTimeout(() => setTransitioning(false), 520)
  }
  return { pathname, navigate, transitioning }
}

export default function App() {
  const { pathname, navigate, transitioning } = usePathname()
  const Page = ROUTES[pathname] || HomePage
  return <SiteLayout pathname={pathname} navigate={navigate}>
    {transitioning && <div className="page-loader" role="status" aria-label="Loading page"><div className="loader-mark"><span>LE</span><i /><i /><i /></div><p>Preparing your workspace</p><div className="loader-line"><span /></div></div>}
    <div className="page-stage" key={pathname}><Page navigate={navigate} /></div>
  </SiteLayout>
}
