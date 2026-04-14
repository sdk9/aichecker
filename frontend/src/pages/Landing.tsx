import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  ShieldCheck, Zap, FileSearch, BarChart3, Download, Cpu,
  Users, ShoppingBag, GraduationCap, Newspaper, Scale,
  ArrowRight, CheckCircle2, Lock, Globe, ImageIcon, Video,
  Music, FileText,
} from 'lucide-react'

const FADE_UP = {
  hidden: { opacity: 0, y: 24 },
  show: (i = 0) => ({ opacity: 1, y: 0, transition: { delay: i * 0.08, duration: 0.5 } }),
}

export default function Landing() {
  return (
    <div className="overflow-x-hidden">
      {/* ── Hero ── */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Background glow */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-indigo-600/10 rounded-full blur-3xl" />
          <div className="absolute top-1/3 left-1/3 w-[400px] h-[400px] bg-purple-600/8 rounded-full blur-3xl" />
          <div
            className="absolute inset-0 opacity-[0.03]"
            style={{
              backgroundImage: 'radial-gradient(circle, #6366f1 1px, transparent 1px)',
              backgroundSize: '40px 40px',
            }}
          />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center py-24">
          <motion.div
            initial="hidden"
            animate="show"
            variants={FADE_UP}
            custom={0}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-600/15 border border-indigo-500/30 text-indigo-300 text-sm font-medium mb-8"
          >
            <Cpu className="w-4 h-4" />
            Forensic AI Content Detection
          </motion.div>

          <motion.h1
            initial="hidden"
            animate="show"
            variants={FADE_UP}
            custom={1}
            className="text-5xl sm:text-6xl lg:text-7xl font-black tracking-tight text-white leading-tight mb-6"
          >
            Is this content
            <br />
            <span className="gradient-text">AI-generated?</span>
          </motion.h1>

          <motion.p
            initial="hidden"
            animate="show"
            variants={FADE_UP}
            custom={2}
            className="text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed"
          >
            Upload images, video, audio, or documents. VeritasAI runs forensic
            analysis — metadata, C2PA credentials, frequency patterns — and gives
            you a confidence score with downloadable evidence report.
          </motion.p>

          <motion.div
            initial="hidden"
            animate="show"
            variants={FADE_UP}
            custom={3}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <Link to="/analyze" className="btn-primary flex items-center justify-center gap-2 text-base px-8 py-4">
              Analyze a File <ArrowRight className="w-4 h-4" />
            </Link>
            <Link to="/api-docs" className="btn-secondary flex items-center justify-center gap-2 text-base px-8 py-4">
              View API Docs
            </Link>
          </motion.div>

          {/* Format pills */}
          <motion.div
            initial="hidden"
            animate="show"
            variants={FADE_UP}
            custom={4}
            className="flex flex-wrap justify-center gap-3 mt-12"
          >
            {[
              { icon: ImageIcon, label: 'Images', color: 'text-blue-400' },
              { icon: Video, label: 'Video', color: 'text-purple-400' },
              { icon: Music, label: 'Audio', color: 'text-pink-400' },
              { icon: FileText, label: 'PDF / DOCX', color: 'text-emerald-400' },
            ].map(({ icon: Icon, label, color }) => (
              <div
                key={label}
                className="flex items-center gap-2 px-4 py-2 rounded-full bg-slate-800/60 border border-slate-700 text-sm text-slate-300"
              >
                <Icon className={`w-4 h-4 ${color}`} />
                {label}
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── How it works ── */}
      <section className="py-24 bg-slate-900/40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">How VeritasAI works</h2>
            <p className="text-slate-400 text-lg max-w-2xl mx-auto">
              Six-layer forensic pipeline — every file is analyzed across multiple independent signals.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: FileSearch,
                step: '01',
                title: 'Metadata Extraction',
                desc: 'Extract EXIF, XMP, ID3, and document metadata. Missing camera info, AI tool references, and stripped tags are red flags.',
                color: 'text-blue-400',
                bg: 'bg-blue-500/10',
              },
              {
                icon: ShieldCheck,
                step: '02',
                title: 'C2PA / Content Credentials',
                desc: 'Parse JUMBF boxes for C2PA provenance manifests. Verify digital signatures, claim generators, and trusted providers.',
                color: 'text-indigo-400',
                bg: 'bg-indigo-500/10',
              },
              {
                icon: Zap,
                step: '03',
                title: 'AI Pattern Detection',
                desc: 'Run Error Level Analysis, DCT frequency analysis, noise uniformity checks, and texture regularity scoring.',
                color: 'text-purple-400',
                bg: 'bg-purple-500/10',
              },
              {
                icon: Cpu,
                step: '04',
                title: 'Manipulation Detection',
                desc: 'Detect splicing, inpainting, and upscaling artifacts. Identify inconsistent compression history across image blocks.',
                color: 'text-pink-400',
                bg: 'bg-pink-500/10',
              },
              {
                icon: BarChart3,
                step: '05',
                title: 'Confidence Scoring',
                desc: 'Weighted ensemble of all signals produces a 0–100% AI probability score with per-signal severity breakdown.',
                color: 'text-amber-400',
                bg: 'bg-amber-500/10',
              },
              {
                icon: Download,
                step: '06',
                title: 'Evidence Report',
                desc: 'Generate a professional PDF chain-of-custody report with metadata tables, signal findings, and legal disclaimers.',
                color: 'text-emerald-400',
                bg: 'bg-emerald-500/10',
              },
            ].map((item, i) => (
              <motion.div
                key={item.step}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.07 }}
                className="card p-6 hover:border-slate-700 transition-colors"
              >
                <div className="flex items-start gap-4">
                  <div className={`${item.bg} rounded-xl p-3 flex-shrink-0`}>
                    <item.icon className={`w-6 h-6 ${item.color}`} />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-slate-500 tracking-widest mb-1">{item.step}</div>
                    <h3 className="font-semibold text-white mb-2">{item.title}</h3>
                    <p className="text-slate-400 text-sm leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Niche use cases ── */}
      <section id="niches" className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">Built for your industry</h2>
            <p className="text-slate-400 text-lg max-w-2xl mx-auto">
              AI fraud looks different in every sector. VeritasAI is tuned for the exact threats your team faces.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[
              {
                icon: Users,
                label: 'HR & Talent',
                color: 'text-blue-400',
                bg: 'bg-blue-500/10',
                border: 'border-blue-500/20',
                headline: 'Screen out synthetic candidates',
                desc: 'Detect AI-generated portfolio images, synthetic voice samples in audio interviews, and deepfake video submissions before they reach a hiring manager.',
                bullets: [
                  'Portfolio photo authenticity check',
                  'Voice sample origin detection',
                  'Video interview deepfake analysis',
                  'Resume photo verification',
                ],
              },
              {
                icon: ShoppingBag,
                label: 'Marketplaces',
                color: 'text-purple-400',
                bg: 'bg-purple-500/10',
                border: 'border-purple-500/20',
                headline: 'Stop fake product listings',
                desc: "AI-generated product photos and seller videos erode buyer trust. VeritasAI flags synthetic imagery at upload time — before it reaches your customers' feed.",
                bullets: [
                  'Product photo AI detection',
                  'Seller profile image checks',
                  'Fake review image scanning',
                  'Bulk API for listing pipelines',
                ],
              },
              {
                icon: GraduationCap,
                label: 'Education',
                color: 'text-emerald-400',
                bg: 'bg-emerald-500/10',
                border: 'border-emerald-500/20',
                headline: 'Identify AI-written assignments',
                desc: 'Analyse submission documents for linguistic patterns, burstiness, vocabulary richness, and AI-typical transition phrases used by GPT-class models.',
                bullets: [
                  'Essay & assignment analysis',
                  'PDF and DOCX support',
                  'Sentence burstiness scoring',
                  'AI phrase density detection',
                ],
              },
              {
                icon: Newspaper,
                label: 'Media & Journalism',
                color: 'text-amber-400',
                bg: 'bg-amber-500/10',
                border: 'border-amber-500/20',
                headline: 'Verify submitted visuals',
                desc: 'Run provenance checks on photos and videos submitted by citizen journalists. Detect manipulated imagery and verify C2PA Content Credentials before publication.',
                bullets: [
                  'C2PA provenance verification',
                  'Photo manipulation detection',
                  'Video frame analysis',
                  'Chain-of-custody reports',
                ],
              },
              {
                icon: Scale,
                label: 'Legal & Compliance',
                color: 'text-rose-400',
                bg: 'bg-rose-500/10',
                border: 'border-rose-500/20',
                headline: 'Evidence-grade forensic reports',
                desc: 'Generate professional PDF reports documenting all detected signals, metadata findings, and confidence scores. Built for evidentiary packaging and audit trails.',
                bullets: [
                  'Downloadable PDF evidence reports',
                  'Job ID chain-of-custody tracking',
                  'Timestamp and analysis metadata',
                  'Multi-signal corroboration',
                ],
              },
              {
                icon: Globe,
                label: 'Enterprise API',
                color: 'text-indigo-400',
                bg: 'bg-indigo-500/10',
                border: 'border-indigo-500/20',
                headline: 'Integrate into your workflow',
                desc: 'REST API with a single POST endpoint. Integrate VeritasAI into your upload pipelines, content moderation stack, or compliance workflows in minutes.',
                bullets: [
                  'REST API, JSON responses',
                  'Multipart file upload',
                  'Niche context hints',
                  'PDF report endpoint',
                ],
              },
            ].map((niche, i) => (
              <motion.div
                key={niche.label}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.07 }}
                className={`card p-7 border ${niche.border} hover:bg-slate-800/30 transition-colors`}
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className={`${niche.bg} rounded-xl p-2.5`}>
                    <niche.icon className={`w-5 h-5 ${niche.color}`} />
                  </div>
                  <span className={`text-xs font-bold uppercase tracking-widest ${niche.color}`}>
                    {niche.label}
                  </span>
                </div>
                <h3 className="text-xl font-bold text-white mb-3">{niche.headline}</h3>
                <p className="text-slate-400 text-sm leading-relaxed mb-5">{niche.desc}</p>
                <ul className="space-y-2">
                  {niche.bullets.map(b => (
                    <li key={b} className="flex items-center gap-2 text-sm text-slate-300">
                      <CheckCircle2 className={`w-4 h-4 flex-shrink-0 ${niche.color}`} />
                      {b}
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Trust signals ── */}
      <section className="py-20 bg-slate-900/40">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[
              { value: '10+', label: 'Detection signals per file' },
              { value: '6', label: 'Analysis layers' },
              { value: 'C2PA', label: 'Content Credentials standard' },
              { value: 'PDF', label: 'Evidence reports' },
            ].map(stat => (
              <div key={stat.label}>
                <div className="text-3xl font-black text-indigo-400 mb-1">{stat.value}</div>
                <div className="text-slate-400 text-sm">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="py-24">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.97 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="card p-12 border-indigo-500/20 relative overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-600/10 via-transparent to-purple-600/10 pointer-events-none" />
            <Lock className="w-10 h-10 text-indigo-400 mx-auto mb-5" />
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              Verify authenticity now
            </h2>
            <p className="text-slate-400 text-lg mb-8 max-w-xl mx-auto">
              Drop a file — image, video, audio, or document — and get a full forensic report in seconds.
            </p>
            <Link to="/analyze" className="btn-primary inline-flex items-center gap-2 text-base px-10 py-4">
              Start Detection <ArrowRight className="w-5 h-5" />
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  )
}
