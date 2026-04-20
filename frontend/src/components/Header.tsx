import { Link, useLocation } from 'react-router-dom'
import { ShieldCheck, Menu, X, User, LogOut, ChevronDown } from 'lucide-react'
import { useState, useRef, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'

export default function Header() {
  const location = useLocation()
  const { user, logout } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [dropOpen, setDropOpen] = useState(false)
  const dropRef = useRef<HTMLDivElement>(null)

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (dropRef.current && !dropRef.current.contains(e.target as Node)) setDropOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const nav = [
    { href: '/', label: 'Home' },
    { href: '/analyze', label: 'Detect' },
    { href: '/pricing', label: 'Pricing' },
    { href: '/contact', label: 'Contact' },
  ]

  const PLAN_BADGE: Record<string, string> = {
    pro: 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30',
    enterprise: 'bg-purple-600/20 text-purple-400 border border-purple-500/30',
  }

  return (
    <header className="sticky top-0 z-50 border-b border-slate-800/60 bg-slate-950/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center group-hover:bg-indigo-500 transition-colors">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-lg text-white">
              Veritas<span className="text-indigo-400">AI</span>
            </span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-1">
            {nav.map(n => (
              <Link
                key={n.href}
                to={n.href}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  location.pathname === n.href
                    ? 'bg-indigo-600/20 text-indigo-400'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800'
                }`}
              >
                {n.label}
              </Link>
            ))}
          </nav>

          {/* Desktop right side */}
          <div className="hidden md:flex items-center gap-3">
            {user ? (
              <div className="relative" ref={dropRef}>
                <button
                  onClick={() => setDropOpen(d => !d)}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
                >
                  <div className="w-6 h-6 bg-indigo-600/30 rounded-full flex items-center justify-center">
                    <User className="w-3.5 h-3.5 text-indigo-400" />
                  </div>
                  <span className="max-w-[120px] truncate">{user.full_name || user.email}</span>
                  {user.plan !== 'free' && (
                    <span className={`text-xs px-1.5 py-0.5 rounded-full capitalize font-medium ${PLAN_BADGE[user.plan]}`}>
                      {user.plan}
                    </span>
                  )}
                  <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
                </button>

                {dropOpen && (
                  <div className="absolute right-0 mt-1 w-48 bg-slate-900 border border-slate-800 rounded-xl shadow-xl py-1 z-50">
                    <Link
                      to="/account"
                      onClick={() => setDropOpen(false)}
                      className="flex items-center gap-2 px-4 py-2.5 text-sm text-slate-300 hover:text-white hover:bg-slate-800"
                    >
                      <User className="w-4 h-4" />
                      My Account
                    </Link>
                    <Link
                      to="/pricing"
                      onClick={() => setDropOpen(false)}
                      className="flex items-center gap-2 px-4 py-2.5 text-sm text-slate-300 hover:text-white hover:bg-slate-800"
                    >
                      <ShieldCheck className="w-4 h-4" />
                      Upgrade Plan
                    </Link>
                    <hr className="border-slate-800 my-1" />
                    <button
                      onClick={() => { logout(); setDropOpen(false) }}
                      className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-slate-400 hover:text-red-400 hover:bg-slate-800"
                    >
                      <LogOut className="w-4 h-4" />
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <>
                <Link to="/login" className="text-sm text-slate-400 hover:text-white transition-colors px-3 py-2">
                  Sign in
                </Link>
                <Link to="/signup" className="btn-primary text-sm py-2">
                  Get started free
                </Link>
              </>
            )}
          </div>

          {/* Mobile toggle */}
          <button
            className="md:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
            onClick={() => setMobileOpen(!mobileOpen)}
          >
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-slate-800 bg-slate-950 px-4 py-4 space-y-1">
          {nav.map(n => (
            <Link
              key={n.href}
              to={n.href}
              onClick={() => setMobileOpen(false)}
              className={`block px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                location.pathname === n.href
                  ? 'bg-indigo-600/20 text-indigo-400'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800'
              }`}
            >
              {n.label}
            </Link>
          ))}
          <hr className="border-slate-800 my-2" />
          {user ? (
            <>
              <Link
                to="/account"
                onClick={() => setMobileOpen(false)}
                className="block px-4 py-3 rounded-lg text-sm text-slate-300 hover:text-white hover:bg-slate-800"
              >
                My Account
              </Link>
              <button
                onClick={() => { logout(); setMobileOpen(false) }}
                className="w-full text-left px-4 py-3 rounded-lg text-sm text-slate-400 hover:text-red-400 hover:bg-slate-800"
              >
                Sign out
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                onClick={() => setMobileOpen(false)}
                className="block px-4 py-3 rounded-lg text-sm text-slate-400 hover:text-white hover:bg-slate-800"
              >
                Sign in
              </Link>
              <Link
                to="/signup"
                onClick={() => setMobileOpen(false)}
                className="btn-primary text-sm block text-center mt-2"
              >
                Get started free
              </Link>
            </>
          )}
        </div>
      )}
    </header>
  )
}
