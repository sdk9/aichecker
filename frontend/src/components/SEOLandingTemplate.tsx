import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, CheckCircle2, ChevronDown } from 'lucide-react'
import { useState } from 'react'
import { useSEO } from '../hooks/useSEO'

export interface SEOFeature {
  icon: string
  title: string
  desc: string
}

export interface SEOFAQ {
  q: string
  a: string
}

export interface SEOLandingConfig {
  title: string
  description: string
  canonical: string
  keywords: string
  schema: object
  badge: string
  heroTitle: string
  heroHighlight: string
  heroSubtitle: string
  ctaLabel: string
  features: SEOFeature[]
  howItWorks: string[]
  faqs: SEOFAQ[]
  relatedLinks: { href: string; label: string }[]
}

const FADE_UP = {
  hidden: { opacity: 0, y: 20 },
  show: (i = 0) => ({ opacity: 1, y: 0, transition: { delay: i * 0.07, duration: 0.45 } }),
}

function FAQItem({ q, a }: SEOFAQ) {
  const [open, setOpen] = useState(false)
  return (
    <div className="border border-slate-800 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-6 py-4 text-left text-slate-200 hover:bg-slate-800/50 transition-colors"
      >
        <span className="font-medium">{q}</span>
        <ChevronDown className={`w-4 h-4 text-slate-500 transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && (
        <div className="px-6 pb-5 text-slate-400 text-sm leading-relaxed border-t border-slate-800 pt-4">
          {a}
        </div>
      )}
    </div>
  )
}

export default function SEOLandingTemplate({ config }: { config: SEOLandingConfig }) {
  useSEO({
    title: config.title,
    description: config.description,
    canonical: config.canonical,
    keywords: config.keywords,
    schema: config.schema,
  })

  return (
    <div className="overflow-x-hidden bg-slate-950">
      {/* Hero */}
      <section className="relative min-h-[80vh] flex items-center justify-center overflow-hidden py-24 px-4">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[700px] h-[500px] bg-indigo-600/10 rounded-full blur-3xl" />
          <div
            className="absolute inset-0 opacity-[0.025]"
            style={{
              backgroundImage: 'radial-gradient(circle, #6366f1 1px, transparent 1px)',
              backgroundSize: '40px 40px',
            }}
          />
        </div>

        <div className="relative max-w-4xl mx-auto text-center">
          <motion.div initial="hidden" animate="show" variants={FADE_UP} custom={0}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-600/15 border border-indigo-500/30 text-indigo-300 text-sm font-medium mb-8">
            {config.badge}
          </motion.div>

          <motion.h1 initial="hidden" animate="show" variants={FADE_UP} custom={1}
            className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-white leading-tight mb-6">
            {config.heroTitle}
            <br />
            <span className="gradient-text">{config.heroHighlight}</span>
          </motion.h1>

          <motion.p initial="hidden" animate="show" variants={FADE_UP} custom={2}
            className="text-lg text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            {config.heroSubtitle}
          </motion.p>

          <motion.div initial="hidden" animate="show" variants={FADE_UP} custom={3}
            className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/analyze" className="btn-primary inline-flex items-center gap-2 px-8 py-3 text-base">
              {config.ctaLabel} <ArrowRight className="w-4 h-4" />
            </Link>
            <Link to="/pricing" className="px-8 py-3 rounded-xl border border-slate-700 text-slate-300 hover:border-indigo-500 hover:text-white transition-colors text-base">
              View Pricing
            </Link>
          </motion.div>

          <motion.p initial="hidden" animate="show" variants={FADE_UP} custom={4}
            className="mt-5 text-slate-500 text-sm">
            Free to try — no credit card required
          </motion.p>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4 bg-slate-900/40 border-t border-slate-800">
        <div className="max-w-6xl mx-auto">
          <motion.h2 initial="hidden" whileInView="show" viewport={{ once: true }} variants={FADE_UP}
            className="text-3xl font-bold text-white text-center mb-4">
            How VeritasAI Detects AI Content
          </motion.h2>
          <motion.p initial="hidden" whileInView="show" viewport={{ once: true }} variants={FADE_UP} custom={1}
            className="text-slate-400 text-center mb-14 max-w-xl mx-auto">
            Multi-layer forensic analysis combining statistical models, metadata inspection, and pattern recognition.
          </motion.p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {config.features.map((f, i) => (
              <motion.div key={i} initial="hidden" whileInView="show" viewport={{ once: true }} variants={FADE_UP} custom={i * 0.5}
                className="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-indigo-500/40 transition-colors">
                <div className="text-3xl mb-4">{f.icon}</div>
                <h3 className="font-semibold text-white mb-2">{f.title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 px-4">
        <div className="max-w-3xl mx-auto">
          <motion.h2 initial="hidden" whileInView="show" viewport={{ once: true }} variants={FADE_UP}
            className="text-3xl font-bold text-white text-center mb-12">
            3 Steps to Detect AI Content
          </motion.h2>
          <div className="space-y-6">
            {config.howItWorks.map((step, i) => (
              <motion.div key={i} initial="hidden" whileInView="show" viewport={{ once: true }} variants={FADE_UP} custom={i * 0.4}
                className="flex items-start gap-4">
                <div className="w-8 h-8 rounded-full bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold text-sm flex-shrink-0">
                  {i + 1}
                </div>
                <p className="text-slate-300 pt-1">{step}</p>
              </motion.div>
            ))}
          </div>
          <motion.div initial="hidden" whileInView="show" viewport={{ once: true }} variants={FADE_UP} custom={2}
            className="mt-10 text-center">
            <Link to="/analyze" className="btn-primary inline-flex items-center gap-2 px-8 py-3">
              Try It Free <ArrowRight className="w-4 h-4" />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-20 px-4 bg-slate-900/40 border-t border-slate-800">
        <div className="max-w-3xl mx-auto">
          <motion.h2 initial="hidden" whileInView="show" viewport={{ once: true }} variants={FADE_UP}
            className="text-3xl font-bold text-white text-center mb-12">
            Frequently Asked Questions
          </motion.h2>
          <div className="space-y-3">
            {config.faqs.map((faq, i) => (
              <motion.div key={i} initial="hidden" whileInView="show" viewport={{ once: true }} variants={FADE_UP} custom={i * 0.3}>
                <FAQItem q={faq.q} a={faq.a} />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Internal links / related tools */}
      <section className="py-16 px-4 border-t border-slate-800">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-xl font-semibold text-slate-300 mb-6">More Detection Tools</h2>
          <div className="flex flex-wrap gap-3 justify-center">
            {config.relatedLinks.map((l, i) => (
              <Link key={i} to={l.href}
                className="px-4 py-2 rounded-lg border border-slate-700 text-slate-400 hover:text-white hover:border-indigo-500 transition-colors text-sm">
                {l.label}
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* CTA strip */}
      <section className="py-16 px-4 bg-indigo-600/10 border-t border-indigo-500/20">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to detect AI content?</h2>
          <p className="text-slate-400 mb-8">Start free — no credit card, no signup required for your first scan.</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/analyze" className="btn-primary inline-flex items-center gap-2 px-8 py-3">
              Start Detecting <ArrowRight className="w-4 h-4" />
            </Link>
            <Link to="/signup" className="px-8 py-3 rounded-xl border border-slate-700 text-slate-300 hover:border-white hover:text-white transition-colors">
              Create Free Account
            </Link>
          </div>
          <div className="mt-6 flex justify-center gap-6 text-sm text-slate-500">
            {['Free plan available', 'No credit card', 'Instant results'].map(t => (
              <span key={t} className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" /> {t}
              </span>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
