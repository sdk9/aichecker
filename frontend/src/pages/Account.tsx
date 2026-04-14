import { useState } from 'react'
import { Navigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  User, CreditCard, ShieldCheck, LogOut, Zap, Building2,
  Sparkles, BarChart3, AlertCircle, CheckCircle2, ExternalLink,
} from 'lucide-react'
import axios from 'axios'
import { useAuth } from '../context/AuthContext'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const PLAN_ICONS: Record<string, any> = { free: Sparkles, pro: Zap, enterprise: Building2 }
const PLAN_COLORS: Record<string, string> = {
  free: 'text-slate-400', pro: 'text-indigo-400', enterprise: 'text-purple-400'
}
const PLAN_BG: Record<string, string> = {
  free: 'bg-slate-500/10', pro: 'bg-indigo-500/10', enterprise: 'bg-purple-500/10'
}

export default function Account() {
  const { user, logout, token, refreshUser } = useAuth()
  const [loadingPortal, setLoadingPortal] = useState(false)
  const [portalError, setPortalError] = useState('')

  const searchParams = new URLSearchParams(window.location.search)
  const upgraded = searchParams.get('upgrade') === 'success'

  if (!user) return <Navigate to="/login" replace />

  const PlanIcon = PLAN_ICONS[user.plan] || Sparkles
  const usagePct = Math.min((user.daily_scans / user.daily_limit) * 100, 100)
  const usageColor = usagePct >= 90 ? 'bg-red-500' : usagePct >= 60 ? 'bg-amber-500' : 'bg-indigo-500'

  const openPortal = async () => {
    if (user.plan === 'free') return
    setPortalError('')
    setLoadingPortal(true)
    try {
      const { data } = await axios.post(
        `${API}/api/billing/portal`,
        {},
        { headers: { Authorization: `Bearer ${token}` } },
      )
      window.location.href = data.url
    } catch (err: any) {
      setPortalError(err?.response?.data?.detail || 'Could not open billing portal')
    } finally {
      setLoadingPortal(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 py-16 px-4">
      <div className="max-w-3xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>

          {/* Welcome banner */}
          {upgraded && (
            <div className="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm rounded-lg px-4 py-3 mb-6">
              <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
              Upgrade successful! Your plan is now active.
            </div>
          )}

          {/* Page header */}
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-2xl font-bold text-white">My Account</h1>
            <button
              onClick={logout}
              className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-white transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Sign out
            </button>
          </div>

          <div className="space-y-5">
            {/* Profile card */}
            <div className="card p-6">
              <div className="flex items-center gap-3 mb-5">
                <div className="w-8 h-8 bg-indigo-500/10 rounded-lg flex items-center justify-center">
                  <User className="w-4 h-4 text-indigo-400" />
                </div>
                <h2 className="font-semibold text-white">Profile</h2>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-slate-500 mb-0.5">Email</p>
                  <p className="text-slate-200">{user.email}</p>
                </div>
                {user.full_name && (
                  <div>
                    <p className="text-slate-500 mb-0.5">Name</p>
                    <p className="text-slate-200">{user.full_name}</p>
                  </div>
                )}
                <div>
                  <p className="text-slate-500 mb-0.5">Member since</p>
                  <p className="text-slate-200">
                    {new Date(user.created_at).toLocaleDateString('en-US', {
                      year: 'numeric', month: 'long', day: 'numeric',
                    })}
                  </p>
                </div>
              </div>
            </div>

            {/* Usage card */}
            <div className="card p-6">
              <div className="flex items-center gap-3 mb-5">
                <div className="w-8 h-8 bg-indigo-500/10 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-4 h-4 text-indigo-400" />
                </div>
                <h2 className="font-semibold text-white">Today's usage</h2>
              </div>
              <div className="flex items-end justify-between mb-2">
                <span className="text-slate-400 text-sm">Scans used</span>
                <span className="text-white font-semibold text-sm">
                  {user.daily_scans} / {user.daily_limit >= 9999 ? '∞' : user.daily_limit}
                </span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-2 rounded-full transition-all ${usageColor}`}
                  style={{ width: `${usagePct}%` }}
                />
              </div>
              {usagePct >= 90 && user.plan === 'free' && (
                <p className="text-amber-400 text-xs mt-2">
                  Almost at your daily limit.{' '}
                  <Link to="/pricing" className="underline">Upgrade for more scans.</Link>
                </p>
              )}
            </div>

            {/* Plan card */}
            <div className="card p-6">
              <div className="flex items-center gap-3 mb-5">
                <div className="w-8 h-8 bg-indigo-500/10 rounded-lg flex items-center justify-center">
                  <CreditCard className="w-4 h-4 text-indigo-400" />
                </div>
                <h2 className="font-semibold text-white">Subscription</h2>
              </div>

              <div className="flex items-center gap-3 mb-5">
                <div className={`${PLAN_BG[user.plan]} w-10 h-10 rounded-xl flex items-center justify-center`}>
                  <PlanIcon className={`w-5 h-5 ${PLAN_COLORS[user.plan]}`} />
                </div>
                <div>
                  <p className="font-semibold text-white capitalize">{user.plan} Plan</p>
                  <p className="text-slate-400 text-sm">
                    {user.daily_limit >= 9999 ? 'Unlimited' : user.daily_limit} scans/day
                  </p>
                </div>
              </div>

              {portalError && (
                <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 text-red-400 text-sm rounded-lg px-3 py-2 mb-4">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  {portalError}
                </div>
              )}

              <div className="flex flex-col sm:flex-row gap-3">
                {user.plan === 'free' ? (
                  <Link to="/pricing" className="btn-primary text-sm py-2 text-center">
                    Upgrade plan
                  </Link>
                ) : (
                  <button
                    onClick={openPortal}
                    disabled={loadingPortal}
                    className="flex items-center justify-center gap-1.5 btn-secondary text-sm py-2 disabled:opacity-60"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    {loadingPortal ? 'Opening…' : 'Manage billing'}
                  </button>
                )}
              </div>
            </div>

            {/* Security card */}
            <div className="card p-6">
              <div className="flex items-center gap-3 mb-5">
                <div className="w-8 h-8 bg-indigo-500/10 rounded-lg flex items-center justify-center">
                  <ShieldCheck className="w-4 h-4 text-indigo-400" />
                </div>
                <h2 className="font-semibold text-white">Security</h2>
              </div>
              <Link
                to="/forgot-password"
                className="text-indigo-400 hover:text-indigo-300 text-sm font-medium"
              >
                Change password →
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
