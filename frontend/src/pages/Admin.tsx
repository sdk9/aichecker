import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import axios from 'axios'
import {
  Users, TrendingUp, DollarSign, Activity, Search, ChevronLeft, ChevronRight,
  Shield, Trash2, RefreshCw, BarChart2, UserCheck, UserX, Crown,
  AlertTriangle, CheckCircle, Clock, Filter, Eye, Globe,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const PLAN_COLOR: Record<string, string> = {
  free: 'bg-slate-700 text-slate-300',
  pro: 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/40',
  enterprise: 'bg-purple-600/30 text-purple-300 border border-purple-500/40',
}

interface Stats {
  users: {
    total: number; active: number; inactive: number
    free: number; pro: number; enterprise: number
    new_last_7d: number; new_last_30d: number; with_stripe: number
  }
  scans: { total_all_time: number; this_month: number }
  revenue: { monthly_mrr_cents: number; monthly_mrr_usd: number }
  visitors: {
    today: number; last_7d: number; last_30d: number
    pageviews_today: number; pageviews_total: number
  }
}

interface UserRow {
  id: number; email: string; full_name: string | null; plan: string
  is_active: boolean; is_verified: boolean; daily_scans: number
  last_scan_date: string | null; created_at: string
  stripe_customer_id?: string; stripe_subscription_id?: string
}

interface UserList {
  total: number; page: number; per_page: number; pages: number; users: UserRow[]
}

interface Signup { date: string; signups: number }

function StatCard({ icon: Icon, label, value, sub, color = 'text-indigo-400' }: {
  icon: any; label: string; value: string | number; sub?: string; color?: string
}) {
  return (
    <div className="card p-5 flex items-start gap-4">
      <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center flex-shrink-0">
        <Icon className={`w-5 h-5 ${color}`} />
      </div>
      <div>
        <p className="text-slate-400 text-xs mb-0.5">{label}</p>
        <p className="text-2xl font-black text-white">{value}</p>
        {sub && <p className="text-slate-500 text-xs mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}

export default function Admin() {
  const { user, token } = useAuth()
  const navigate = useNavigate()

  const [stats, setStats] = useState<Stats | null>(null)
  const [userList, setUserList] = useState<UserList | null>(null)
  const [signups, setSignups] = useState<Signup[]>([])
  const [visitors, setVisitors] = useState<{ date: string; visitors: number }[]>([])
  const [activity, setActivity] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [planFilter, setPlanFilter] = useState('')
  const [page, setPage] = useState(1)
  const [editUser, setEditUser] = useState<UserRow | null>(null)
  const [editPlan, setEditPlan] = useState('')
  const [editActive, setEditActive] = useState(true)
  const [saving, setSaving] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState<UserRow | null>(null)
  const [tab, setTab] = useState<'overview' | 'users' | 'activity'>('overview')
  const [error, setError] = useState('')

  const headers = { Authorization: `Bearer ${token}` }

  const fetchAll = useCallback(async () => {
    try {
      const [s, u, sg, v, a] = await Promise.all([
        axios.get(`${API}/api/admin/stats`, { headers }),
        axios.get(`${API}/api/admin/users`, {
          params: { page, per_page: 50, search: search || undefined, plan: planFilter || undefined },
          headers,
        }),
        axios.get(`${API}/api/admin/signups/daily`, { params: { days: 30 }, headers }),
        axios.get(`${API}/api/admin/visitors/daily`, { params: { days: 30 }, headers }),
        axios.get(`${API}/api/admin/activity`, { params: { limit: 20 }, headers }),
      ])
      setStats(s.data)
      setUserList(u.data)
      setSignups(sg.data)
      setVisitors(v.data)
      setActivity(a.data)
      setError('')
    } catch (e: any) {
      if (e?.response?.status === 403) navigate('/')
      setError(e?.response?.data?.detail || 'Failed to load admin data')
    } finally {
      setLoading(false)
    }
  }, [page, search, planFilter, token])

  useEffect(() => { fetchAll() }, [fetchAll])

  // Debounce search
  useEffect(() => {
    const t = setTimeout(() => { setPage(1); fetchAll() }, 400)
    return () => clearTimeout(t)
  }, [search, planFilter])

  const handleSaveUser = async () => {
    if (!editUser) return
    setSaving(true)
    try {
      await axios.patch(`${API}/api/admin/users/${editUser.id}`,
        { plan: editPlan, is_active: editActive }, { headers })
      setEditUser(null)
      fetchAll()
    } catch {
      alert('Failed to update user')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!confirmDelete) return
    try {
      await axios.delete(`${API}/api/admin/users/${confirmDelete.id}`, { headers })
      setConfirmDelete(null)
      fetchAll()
    } catch (e: any) {
      alert(e?.response?.data?.detail || 'Delete failed')
    }
  }

  const maxSignups = Math.max(...signups.map(s => s.signups), 1)

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-950 py-8 px-4">
      <div className="max-w-7xl mx-auto">

        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-black text-white flex items-center gap-2">
              <Crown className="w-6 h-6 text-amber-400" /> Admin Dashboard
            </h1>
            <p className="text-slate-500 text-sm mt-0.5">Signed in as {user?.email}</p>
          </div>
          <button
            onClick={() => { setLoading(true); fetchAll() }}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 text-slate-300 hover:text-white text-sm transition-colors"
          >
            <RefreshCw className="w-4 h-4" /> Refresh
          </button>
        </div>

        {error && (
          <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 text-red-400 text-sm rounded-lg px-4 py-3 mb-6">
            <AlertTriangle className="w-4 h-4" /> {error}
          </div>
        )}

        {/* Tab bar */}
        <div className="flex gap-1 mb-8 bg-slate-900 rounded-xl p-1 w-fit">
          {(['overview', 'users', 'activity'] as const).map(t => (
            <button key={t} onClick={() => setTab(t)}
              className={`px-5 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${
                tab === t ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        {/* ── OVERVIEW TAB ── */}
        {tab === 'overview' && stats && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>

            {/* Visitor KPIs */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <StatCard icon={Globe} label="Visitors Today" value={stats.visitors?.today ?? 0} color="text-cyan-400"
                sub={`${stats.visitors?.pageviews_today ?? 0} page views`} />
              <StatCard icon={Eye} label="Visitors (7 days)" value={stats.visitors?.last_7d ?? 0} color="text-teal-400" />
              <StatCard icon={TrendingUp} label="Visitors (30 days)" value={stats.visitors?.last_30d ?? 0} color="text-sky-400" />
              <StatCard icon={BarChart2} label="Total Page Views" value={stats.visitors?.pageviews_total ?? 0} color="text-indigo-400" />
            </div>

            {/* User KPI grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <StatCard icon={Users} label="Total Users" value={stats.users.total} sub={`+${stats.users.new_last_7d} this week`} />
              <StatCard icon={Crown} label="Pro Users" value={stats.users.pro} color="text-amber-400"
                sub={`${stats.users.enterprise} enterprise`} />
              <StatCard icon={DollarSign} label="MRR" value={`$${stats.revenue.monthly_mrr_usd}`} color="text-green-400"
                sub={`${stats.users.pro} paying users`} />
              <StatCard icon={Activity} label="Scans This Month" value={stats.scans.this_month}
                sub={`${stats.scans.total_all_time} all time`} color="text-purple-400" />
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
              <StatCard icon={UserCheck} label="Active Accounts" value={stats.users.active} color="text-green-400" />
              <StatCard icon={UserX} label="Inactive Accounts" value={stats.users.inactive} color="text-red-400" />
              <StatCard icon={TrendingUp} label="New (30 days)" value={stats.users.new_last_30d} color="text-sky-400" />
              <StatCard icon={BarChart2} label="Stripe Accounts" value={stats.users.with_stripe}
                sub="ever attempted upgrade" color="text-indigo-400" />
            </div>

            {/* Visitors chart */}
            <div className="card p-6 mb-6">
              <h2 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
                <Globe className="w-4 h-4 text-cyan-400" /> Daily Unique Visitors (last 30 days)
              </h2>
              {visitors.length === 0 ? (
                <p className="text-slate-500 text-sm">No visitor data yet — tracking starts now.</p>
              ) : (
                <div className="flex items-end gap-0.5 h-28">
                  {(() => { const max = Math.max(...visitors.map(v => v.visitors), 1); return visitors.slice(-30).map(v => (
                    <div key={v.date} className="flex-1 flex flex-col items-center gap-1 group relative">
                      <div
                        className="w-full bg-cyan-500/60 hover:bg-cyan-400 rounded-sm transition-colors cursor-pointer"
                        style={{ height: `${Math.max((v.visitors / max) * 100, 4)}%` }}
                        title={`${v.date}: ${v.visitors} visitor${v.visitors !== 1 ? 's' : ''}`}
                      />
                      <div className="absolute -top-7 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-xs px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap z-10 pointer-events-none">
                        {v.date.slice(5)}: {v.visitors}
                      </div>
                    </div>
                  ))})()}
                </div>
              )}
            </div>

            {/* Plan breakdown */}
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="card p-6">
                <h2 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
                  <BarChart2 className="w-4 h-4 text-indigo-400" /> Plan Breakdown
                </h2>
                <div className="space-y-3">
                  {[
                    { label: 'Free', value: stats.users.free, total: stats.users.total, color: 'bg-slate-500' },
                    { label: 'Pro', value: stats.users.pro, total: stats.users.total, color: 'bg-indigo-500' },
                    { label: 'Enterprise', value: stats.users.enterprise, total: stats.users.total, color: 'bg-purple-500' },
                  ].map(({ label, value, total, color }) => (
                    <div key={label}>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-400">{label}</span>
                        <span className="text-slate-300">{value} ({total ? Math.round(value / total * 100) : 0}%)</span>
                      </div>
                      <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                        <div className={`h-full ${color} rounded-full`}
                          style={{ width: `${total ? (value / total * 100) : 0}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Signups chart */}
              <div className="card p-6">
                <h2 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-green-400" /> Daily Signups (last 30 days)
                </h2>
                {signups.length === 0 ? (
                  <p className="text-slate-500 text-sm">No signup data yet.</p>
                ) : (
                  <div className="flex items-end gap-0.5 h-28">
                    {signups.slice(-30).map(s => (
                      <div key={s.date} className="flex-1 flex flex-col items-center gap-1 group relative">
                        <div
                          className="w-full bg-indigo-500/60 hover:bg-indigo-400 rounded-sm transition-colors cursor-pointer"
                          style={{ height: `${Math.max((s.signups / maxSignups) * 100, 4)}%` }}
                          title={`${s.date}: ${s.signups} signup${s.signups !== 1 ? 's' : ''}`}
                        />
                        <div className="absolute -top-7 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-xs px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap z-10 pointer-events-none">
                          {s.date.slice(5)}: {s.signups}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

          </motion.div>
        )}

        {/* ── USERS TAB ── */}
        {tab === 'users' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>

            {/* Search + filter */}
            <div className="flex flex-col sm:flex-row gap-3 mb-5">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  placeholder="Search by email or name…"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-9 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div className="relative">
                <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <select
                  value={planFilter}
                  onChange={e => setPlanFilter(e.target.value)}
                  className="bg-slate-900 border border-slate-700 rounded-xl pl-9 pr-8 py-2.5 text-sm text-white appearance-none focus:outline-none focus:border-indigo-500"
                >
                  <option value="">All plans</option>
                  <option value="free">Free</option>
                  <option value="pro">Pro</option>
                  <option value="enterprise">Enterprise</option>
                </select>
              </div>
            </div>

            {userList && (
              <>
                <p className="text-slate-500 text-xs mb-3">{userList.total} users found</p>

                <div className="card overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-slate-800 text-left">
                          {['ID', 'Email', 'Name', 'Plan', 'Scans', 'Active', 'Joined', 'Actions'].map(h => (
                            <th key={h} className="px-4 py-3 text-slate-400 font-medium text-xs">{h}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {userList.users.map(u => (
                          <tr key={u.id} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                            <td className="px-4 py-3 text-slate-500">#{u.id}</td>
                            <td className="px-4 py-3 text-white font-medium max-w-[180px] truncate">{u.email}</td>
                            <td className="px-4 py-3 text-slate-300 max-w-[120px] truncate">{u.full_name || '—'}</td>
                            <td className="px-4 py-3">
                              <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${PLAN_COLOR[u.plan] || 'bg-slate-700 text-slate-300'}`}>
                                {u.plan}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-slate-300">{u.daily_scans}</td>
                            <td className="px-4 py-3">
                              {u.is_active
                                ? <CheckCircle className="w-4 h-4 text-green-400" />
                                : <AlertTriangle className="w-4 h-4 text-red-400" />}
                            </td>
                            <td className="px-4 py-3 text-slate-500 text-xs">
                              {u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}
                            </td>
                            <td className="px-4 py-3">
                              <div className="flex items-center gap-2">
                                <button
                                  onClick={() => { setEditUser(u); setEditPlan(u.plan); setEditActive(u.is_active) }}
                                  className="p-1.5 rounded-lg bg-slate-700 hover:bg-indigo-600/30 text-slate-400 hover:text-indigo-300 transition-colors"
                                  title="Edit"
                                >
                                  <Shield className="w-3.5 h-3.5" />
                                </button>
                                <button
                                  onClick={() => setConfirmDelete(u)}
                                  className="p-1.5 rounded-lg bg-slate-700 hover:bg-red-600/30 text-slate-400 hover:text-red-300 transition-colors"
                                  title="Delete"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Pagination */}
                  {userList.pages > 1 && (
                    <div className="flex items-center justify-between px-4 py-3 border-t border-slate-800">
                      <p className="text-slate-500 text-xs">Page {page} of {userList.pages}</p>
                      <div className="flex gap-2">
                        <button
                          onClick={() => setPage(p => Math.max(1, p - 1))}
                          disabled={page === 1}
                          className="p-1.5 rounded-lg bg-slate-800 disabled:opacity-40 text-slate-400 hover:text-white transition-colors"
                        >
                          <ChevronLeft className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => setPage(p => Math.min(userList.pages, p + 1))}
                          disabled={page === userList.pages}
                          className="p-1.5 rounded-lg bg-slate-800 disabled:opacity-40 text-slate-400 hover:text-white transition-colors"
                        >
                          <ChevronRight className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}
          </motion.div>
        )}

        {/* ── ACTIVITY TAB ── */}
        {tab === 'activity' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="card overflow-hidden">
              <div className="px-5 py-4 border-b border-slate-800">
                <h2 className="text-sm font-semibold text-white flex items-center gap-2">
                  <Clock className="w-4 h-4 text-slate-400" /> Recent Scan Activity
                </h2>
              </div>
              <div className="divide-y divide-slate-800">
                {activity.length === 0 ? (
                  <p className="text-slate-500 text-sm p-5">No activity yet.</p>
                ) : activity.map((a, i) => (
                  <div key={i} className="flex items-center justify-between px-5 py-3 hover:bg-slate-800/30 transition-colors">
                    <div>
                      <p className="text-sm text-white font-medium">{a.email}</p>
                      <p className="text-xs text-slate-500">
                        {a.last_active ? new Date(a.last_active).toLocaleString() : '—'}
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${PLAN_COLOR[a.plan] || ''}`}>
                        {a.plan}
                      </span>
                      <span className="text-slate-400 text-xs">{a.scans} scan{a.scans !== 1 ? 's' : ''}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* ── Edit User Modal ── */}
      {editUser && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="card p-6 w-full max-w-sm">
            <h3 className="text-white font-bold mb-1">Edit User</h3>
            <p className="text-slate-400 text-sm mb-5">{editUser.email}</p>

            <label className="block text-xs text-slate-400 mb-1">Plan</label>
            <select
              value={editPlan}
              onChange={e => setEditPlan(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white mb-4 focus:outline-none focus:border-indigo-500"
            >
              <option value="free">Free</option>
              <option value="pro">Pro</option>
              <option value="enterprise">Enterprise</option>
            </select>

            <label className="flex items-center gap-3 cursor-pointer mb-6">
              <div
                onClick={() => setEditActive(v => !v)}
                className={`w-10 h-5 rounded-full transition-colors relative ${editActive ? 'bg-indigo-600' : 'bg-slate-700'}`}
              >
                <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full transition-transform ${editActive ? 'translate-x-5' : 'translate-x-0.5'}`} />
              </div>
              <span className="text-sm text-slate-300">{editActive ? 'Active' : 'Disabled'}</span>
            </label>

            <div className="flex gap-3">
              <button
                onClick={() => setEditUser(null)}
                className="flex-1 py-2.5 rounded-lg bg-slate-800 text-slate-300 text-sm hover:bg-slate-700 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveUser}
                disabled={saving}
                className="flex-1 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold transition-colors disabled:opacity-50"
              >
                {saving ? 'Saving…' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Delete Confirm Modal ── */}
      {confirmDelete && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="card p-6 w-full max-w-sm">
            <div className="w-10 h-10 rounded-xl bg-red-500/10 flex items-center justify-center mb-4">
              <Trash2 className="w-5 h-5 text-red-400" />
            </div>
            <h3 className="text-white font-bold mb-1">Delete user?</h3>
            <p className="text-slate-400 text-sm mb-5">
              This will permanently delete <strong className="text-white">{confirmDelete.email}</strong>. This cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setConfirmDelete(null)}
                className="flex-1 py-2.5 rounded-lg bg-slate-800 text-slate-300 text-sm hover:bg-slate-700 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                className="flex-1 py-2.5 rounded-lg bg-red-600 hover:bg-red-500 text-white text-sm font-semibold transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
