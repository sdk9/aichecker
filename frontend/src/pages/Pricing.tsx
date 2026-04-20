import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { CheckCircle2, Zap, Building2, Sparkles, AlertCircle } from 'lucide-react'
import axios from 'axios'
import { useAuth } from '../context/AuthContext'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const STRIPE_PRO_LINK = 'https://buy.stripe.com/14A3cxffy7n6fZn9hvcIE00'

interface Plan {
  id: string
  name: string
  price: number
  currency: string
  interval: string | null
  scans_per_day: number
  features: string[]
  stripe_price_id: string | null
  cta: string
}

const ICONS: Record<string, any> = {
  free: Sparkles,
  pro: Zap,
  enterprise: Building2,
}

const COLORS: Record<string, string> = {
  free: 'text-slate-400',
  pro: 'text-indigo-400',
  enterprise: 'text-purple-400',
}

const BG: Record<string, string> = {
  free: 'bg-slate-500/10',
  pro: 'bg-indigo-500/10',
  enterprise: 'bg-purple-500/10',
}

const BORDER: Record<string, string> = {
  free: 'border-slate-700',
  pro: 'border-indigo-500/50',
  enterprise: 'border-purple-500/50',
}

export default function Pricing() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [plans, setPlans] = useState<Plan[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const searchParams = new URLSearchParams(window.location.search)
  const cancelled = searchParams.get('upgrade') === 'cancelled'

  useEffect(() => {
    axios.get(`${API}/api/billing/plans`)
      .then(r => setPlans(r.data.plans))
      .finally(() => setLoading(false))
  }, [])

  const handleSelect = (plan: Plan) => {
    if (plan.id === 'free') return
    if (!user) { navigate('/signup', { state: { from: '/pricing' } }); return }
    if (plan.id === 'enterprise') {
      window.location.href = 'mailto:contact@veritasartificialis.com?subject=Enterprise%20Plan'
      return
    }
    if (plan.id === 'pro') {
      const url = `${STRIPE_PRO_LINK}?prefilled_email=${encodeURIComponent(user.email)}&client_reference_id=${user.id}`
      window.location.href = url
    }
  }

  const fmt = (cents: number) =>
    cents === 0 ? 'Free' : `$${(cents / 100).toFixed(0)}`

  return (
    <div className="min-h-screen bg-slate-950 py-20 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-14">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-600/15 border border-indigo-500/30 text-indigo-300 text-sm font-medium mb-6"
          >
            <Zap className="w-4 h-4" />
            Simple, transparent pricing
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="text-4xl sm:text-5xl font-black text-white mb-4"
          >
            Choose your plan
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-slate-400 text-lg max-w-xl mx-auto"
          >
            Start free. Upgrade when you need more scans or API access.
          </motion.p>
        </div>

        {cancelled && (
          <div className="flex items-center gap-2 bg-amber-500/10 border border-amber-500/30 text-amber-400 text-sm rounded-lg px-4 py-3 mb-8 max-w-xl mx-auto">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            Checkout was cancelled — your plan hasn't changed.
          </div>
        )}
        {error && (
          <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 text-red-400 text-sm rounded-lg px-4 py-3 mb-8 max-w-xl mx-auto">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {/* Plan cards */}
        {loading ? (
          <div className="flex justify-center py-20">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {plans.map((plan, i) => {
              const Icon = ICONS[plan.id] || Sparkles
              const isCurrent = user?.plan === plan.id
              const isPro = plan.id === 'pro'

              return (
                <motion.div
                  key={plan.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.07 }}
                  className={`card p-7 border ${BORDER[plan.id]} ${isPro ? 'ring-1 ring-indigo-500/40' : ''} relative`}
                >
                  {isPro && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-indigo-600 text-white text-xs font-bold px-3 py-1 rounded-full">
                      Most popular
                    </div>
                  )}

                  {/* Plan icon + name */}
                  <div className={`${BG[plan.id]} w-10 h-10 rounded-xl flex items-center justify-center mb-4`}>
                    <Icon className={`w-5 h-5 ${COLORS[plan.id]}`} />
                  </div>
                  <h2 className="text-lg font-bold text-white mb-1">{plan.name}</h2>
                  <p className="text-slate-400 text-sm mb-4">
                    {plan.scans_per_day >= 9999 ? 'Unlimited scans' : `${plan.scans_per_day} scan/month`}
                  </p>

                  {/* Price */}
                  <div className="mb-6">
                    <span className="text-4xl font-black text-white">{fmt(plan.price)}</span>
                    {plan.interval && (
                      <span className="text-slate-400 text-sm ml-1">/{plan.interval}</span>
                    )}
                  </div>

                  {/* Features */}
                  <ul className="space-y-2.5 mb-8">
                    {plan.features.map(f => (
                      <li key={f} className="flex items-start gap-2 text-sm text-slate-300">
                        <CheckCircle2 className={`w-4 h-4 flex-shrink-0 mt-0.5 ${COLORS[plan.id]}`} />
                        {f}
                      </li>
                    ))}
                  </ul>

                  {/* CTA */}
                  {isCurrent ? (
                    <div className="w-full text-center py-2.5 rounded-lg bg-slate-800 text-slate-400 text-sm font-medium cursor-default">
                      Current plan
                    </div>
                  ) : plan.id === 'free' ? (
                    <div className="w-full text-center py-2.5 rounded-lg bg-slate-800 text-slate-400 text-sm font-medium cursor-default">
                      Always free
                    </div>
                  ) : (
                    <button
                      onClick={() => handleSelect(plan)}
                      className={`w-full py-2.5 rounded-lg text-sm font-semibold transition-colors ${
                        isPro
                          ? 'bg-indigo-600 hover:bg-indigo-500 text-white'
                          : 'bg-purple-600 hover:bg-purple-500 text-white'
                      }`}
                    >
                      {plan.cta}
                    </button>
                  )}
                </motion.div>
              )
            })}
          </div>
        )}

        <p className="text-center text-slate-500 text-xs mt-10">
          Payments secured by Stripe. Cancel anytime from your account settings.
        </p>
      </div>
    </div>
  )
}
