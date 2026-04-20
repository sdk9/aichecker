import { motion } from 'framer-motion'
import { Mail, MessageSquare, HelpCircle, Lightbulb, ShieldCheck } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useSEO } from '../hooks/useSEO'

export default function Contact() {
  useSEO({
    title: 'Contact VeritasAI — Get Support & Send Feedback',
    description: 'Contact the VeritasAI team for support, feature requests, partnerships, or any questions about our AI content detection platform.',
    canonical: 'https://veritasartificialis.com/contact',
    keywords: 'contact VeritasAI, AI detector support, AI detection help',
    schema: {
      '@context': 'https://schema.org',
      '@type': 'ContactPage',
      name: 'Contact VeritasAI',
      url: 'https://veritasartificialis.com/contact',
      description: 'Contact the VeritasAI team for support and feedback.',
    },
  })

  return (
    <div className="min-h-screen py-20 px-4 sm:px-6 lg:px-8 bg-slate-950">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-600/15 border border-indigo-500/30 text-indigo-300 text-sm font-medium mb-6">
            <Mail className="w-4 h-4" />
            Get in Touch
          </div>
          <h1 className="text-4xl font-black text-white mb-4">Contact Us</h1>
          <p className="text-slate-400 text-lg">
            We're here to help. Reach out for support, feedback, or anything else.
          </p>
        </motion.div>

        {/* Contact card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card p-8 mb-8 text-center"
        >
          <div className="w-16 h-16 bg-indigo-600/20 rounded-2xl flex items-center justify-center mx-auto mb-5">
            <Mail className="w-8 h-8 text-indigo-400" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-3">Send us an email</h2>
          <p className="text-slate-400 text-sm leading-relaxed mb-6">
            Our team typically responds within 24–48 hours on business days.
          </p>
          <a
            href="mailto:contact@veritasartificialis.com"
            className="btn-primary inline-flex items-center gap-2 px-8 py-3 text-base"
          >
            <Mail className="w-5 h-5" />
            contact@veritasartificialis.com
          </a>
        </motion.div>

        {/* Reason cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10">
          {[
            {
              icon: HelpCircle,
              title: 'Support',
              desc: 'Need help with a scan, your account, or the service?',
              color: 'text-blue-400',
              bg: 'bg-blue-500/10',
            },
            {
              icon: Lightbulb,
              title: 'Suggestions',
              desc: 'Have an idea for a new feature or improvement?',
              color: 'text-amber-400',
              bg: 'bg-amber-500/10',
            },
            {
              icon: MessageSquare,
              title: 'Issues',
              desc: 'Found a bug or unexpected result? Let us know.',
              color: 'text-emerald-400',
              bg: 'bg-emerald-500/10',
            },
          ].map(item => (
            <motion.div
              key={item.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="card p-5 text-center"
            >
              <div className={`${item.bg} w-10 h-10 rounded-xl flex items-center justify-center mx-auto mb-3`}>
                <item.icon className={`w-5 h-5 ${item.color}`} />
              </div>
              <h3 className="font-semibold text-slate-200 text-sm mb-1">{item.title}</h3>
              <p className="text-slate-500 text-xs leading-relaxed">{item.desc}</p>
            </motion.div>
          ))}
        </div>

        {/* Note */}
        <div className="flex items-start gap-3 p-5 rounded-xl bg-slate-900/60 border border-slate-800 mb-8">
          <ShieldCheck className="w-5 h-5 text-indigo-400 flex-shrink-0 mt-0.5" />
          <p className="text-slate-400 text-sm leading-relaxed">
            For billing disputes or cancellation requests, please include your registered email address
            and a brief description of the issue. We'll get back to you as soon as possible.
          </p>
        </div>

        <div className="text-center">
          <Link to="/" className="btn-secondary text-sm px-6 py-2.5">
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  )
}
