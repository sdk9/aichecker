import { motion } from 'framer-motion'
import { AnalysisResult, SignalSeverity } from '../types/analysis'
import {
  Download, RotateCcw, ShieldCheck, ShieldAlert, ShieldX,
  AlertTriangle, CheckCircle2, Info, ChevronDown, ChevronUp,
  Clock, FileType, HardDrive,
} from 'lucide-react'
import { useState } from 'react'
import { RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis } from 'recharts'

interface Props {
  result: AnalysisResult
  onReset: () => void
}

const VERDICT_CONFIG = {
  red: {
    label: 'AI-Generated',
    icon: ShieldX,
    bg: 'bg-red-900/20',
    border: 'border-red-500/40',
    text: 'text-red-400',
    bar: '#ef4444',
    ring: 'ring-red-500/20',
  },
  orange: {
    label: 'Likely AI-Generated',
    icon: ShieldAlert,
    bg: 'bg-orange-900/20',
    border: 'border-orange-500/40',
    text: 'text-orange-400',
    bar: '#f97316',
    ring: 'ring-orange-500/20',
  },
  yellow: {
    label: 'Uncertain',
    icon: AlertTriangle,
    bg: 'bg-yellow-900/20',
    border: 'border-yellow-500/40',
    text: 'text-yellow-400',
    bar: '#eab308',
    ring: 'ring-yellow-500/20',
  },
  green: {
    label: 'Likely Authentic',
    icon: ShieldCheck,
    bg: 'bg-emerald-900/20',
    border: 'border-emerald-500/40',
    text: 'text-emerald-400',
    bar: '#22c55e',
    ring: 'ring-emerald-500/20',
  },
}

const SEVERITY_CONFIG: Record<SignalSeverity, { color: string; bg: string; label: string }> = {
  high: { color: 'text-red-400', bg: 'bg-red-500/15', label: 'HIGH' },
  medium: { color: 'text-orange-400', bg: 'bg-orange-500/15', label: 'MED' },
  low: { color: 'text-emerald-400', bg: 'bg-emerald-500/15', label: 'LOW' },
}

function ScoreGauge({ value, color, label }: { value: number; color: string; label: string }) {
  const pct = Math.round(value * 100)
  const data = [{ value: pct, fill: color }]

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-28 h-28">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            innerRadius="65%"
            outerRadius="100%"
            data={data}
            startAngle={90}
            endAngle={-270}
          >
            <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
            <RadialBar dataKey="value" background={{ fill: '#1e293b' }} cornerRadius={6} />
          </RadialBarChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xl font-black text-white">{pct}<span className="text-sm font-normal text-slate-400">%</span></span>
        </div>
      </div>
      <span className="text-xs text-slate-400 mt-1 text-center">{label}</span>
    </div>
  )
}

export default function ResultsDashboard({ result, onReset }: Props) {
  const [expandedSignals, setExpandedSignals] = useState<Set<number>>(new Set())
  const [metaExpanded, setMetaExpanded] = useState(false)
  const [c2paExpanded, setC2paExpanded] = useState(true)

  const vc = VERDICT_CONFIG[result.verdict_color] ?? VERDICT_CONFIG.yellow
  const VIcon = vc.icon
  const aiPct = Math.round(result.ai_probability * 100)

  const toggleSignal = (i: number) => {
    setExpandedSignals(prev => {
      const next = new Set(prev)
      next.has(i) ? next.delete(i) : next.add(i)
      return next
    })
  }

  const downloadReport = () => {
    window.open(`/api/report/${result.job_id}`, '_blank')
  }

  return (
    <div className="space-y-6">
      {/* Top actions */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">{result.filename}</h1>
          <div className="flex items-center gap-3 mt-1 text-xs text-slate-500">
            <span className="flex items-center gap-1">
              <FileType className="w-3.5 h-3.5" />
              {result.file_type.toUpperCase()} · {result.mime_type}
            </span>
            <span className="flex items-center gap-1">
              <HardDrive className="w-3.5 h-3.5" />
              {(result.file_size_bytes / 1024).toFixed(1)} KB
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              {result.analysis_duration_ms} ms
            </span>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={downloadReport}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition-colors"
          >
            <Download className="w-4 h-4" />
            PDF Report
          </button>
          <button
            onClick={onReset}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium border border-slate-700 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            New File
          </button>
        </div>
      </div>

      {/* Verdict card */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`card p-8 ${vc.border} ${vc.bg} ring-4 ${vc.ring}`}
      >
        <div className="flex flex-col lg:flex-row items-center gap-8">
          {/* Main score */}
          <div className="flex flex-col items-center flex-shrink-0">
            <div className="relative">
              <svg className="w-40 h-40 -rotate-90" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="50" fill="none" stroke="#1e293b" strokeWidth="12" />
                <circle
                  cx="60" cy="60" r="50"
                  fill="none"
                  stroke={vc.bar}
                  strokeWidth="12"
                  strokeLinecap="round"
                  strokeDasharray={`${2 * Math.PI * 50}`}
                  strokeDashoffset={`${2 * Math.PI * 50 * (1 - result.ai_probability)}`}
                  style={{ transition: 'stroke-dashoffset 1s ease' }}
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={`text-4xl font-black ${vc.text}`}>{aiPct}%</span>
                <span className="text-xs text-slate-400 mt-0.5">AI Probability</span>
              </div>
            </div>
          </div>

          {/* Verdict text */}
          <div className="flex-1 text-center lg:text-left">
            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${vc.bg} border ${vc.border} mb-3`}>
              <VIcon className={`w-5 h-5 ${vc.text}`} />
              <span className={`font-bold text-lg ${vc.text}`}>{result.verdict}</span>
            </div>
            <p className="text-slate-300 mb-5">
              Confidence: <strong className="text-white">{Math.round(result.confidence * 100)}%</strong>
              {' '}· {result.signals.filter(s => s.severity === 'high').length} high-severity signals ·
              {' '}{result.signals.filter(s => s.severity === 'medium').length} medium
            </p>

            {/* Sub-score gauges */}
            <div className="flex flex-wrap gap-6 justify-center lg:justify-start">
              <ScoreGauge value={result.metadata_score} color="#6366f1" label="Metadata" />
              <ScoreGauge value={result.artifact_score} color="#a855f7" label="Artifacts" />
              <ScoreGauge value={result.frequency_score} color="#ec4899" label="Frequency" />
              <ScoreGauge value={result.consistency_score} color="#06b6d4" label="Consistency" />
            </div>
          </div>
        </div>
      </motion.div>

      {/* Detection signals */}
      <div className="card overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-indigo-400" />
          <h2 className="font-semibold text-white">Detection Signals</h2>
          <span className="ml-auto text-xs text-slate-500">{result.signals.length} signals</span>
        </div>
        <div className="divide-y divide-slate-800">
          {result.signals.map((sig, i) => {
            const sc = SEVERITY_CONFIG[sig.severity]
            const expanded = expandedSignals.has(i)
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: i * 0.05 }}
              >
                <button
                  onClick={() => toggleSignal(i)}
                  className="w-full px-6 py-4 flex items-start gap-4 hover:bg-slate-800/40 transition-colors text-left"
                >
                  <div className="flex-shrink-0 mt-0.5">
                    <div
                      className="w-2 h-2 rounded-full mt-1"
                      style={{ backgroundColor: sig.severity === 'high' ? '#ef4444' : sig.severity === 'medium' ? '#f97316' : '#22c55e' }}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-1">
                      <span className="font-semibold text-slate-200 text-sm">{sig.name}</span>
                      <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${sc.bg} ${sc.color}`}>
                        {sc.label}
                      </span>
                    </div>
                    <p className="text-slate-400 text-sm">{sig.description}</p>
                    {expanded && sig.details && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        className="mt-3 px-3 py-2 rounded-lg bg-slate-800 border border-slate-700"
                      >
                        <p className="text-xs font-mono text-slate-400">{sig.details}</p>
                      </motion.div>
                    )}
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0">
                    <div className="text-right">
                      <div className="text-sm font-bold text-slate-200">{Math.round(sig.score * 100)}%</div>
                      <div className="text-xs text-slate-500">score</div>
                    </div>
                    {sig.details && (
                      expanded ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />
                    )}
                  </div>
                </button>
              </motion.div>
            )
          })}
        </div>
      </div>

      {/* C2PA */}
      <div className="card overflow-hidden">
        <button
          onClick={() => setC2paExpanded(!c2paExpanded)}
          className="w-full px-6 py-4 border-b border-slate-800 flex items-center gap-2 hover:bg-slate-800/30 transition-colors"
        >
          <ShieldCheck className="w-5 h-5 text-indigo-400" />
          <h2 className="font-semibold text-white">C2PA / Content Credentials</h2>
          <span className={`ml-2 px-2 py-0.5 rounded-full text-xs font-bold ${
            result.c2pa.has_credentials
              ? result.c2pa.trusted ? 'bg-emerald-500/15 text-emerald-400' : 'bg-yellow-500/15 text-yellow-400'
              : 'bg-red-500/15 text-red-400'
          }`}>
            {result.c2pa.has_credentials ? (result.c2pa.trusted ? 'Trusted' : 'Present') : 'None'}
          </span>
          <span className="ml-auto">
            {c2paExpanded ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
          </span>
        </button>
        {c2paExpanded && (
          <div className="px-6 py-5">
            <p className="text-sm text-slate-400 mb-4">{result.c2pa.note}</p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {[
                { label: 'Credentials', value: result.c2pa.has_credentials ? 'Yes' : 'No', ok: result.c2pa.has_credentials },
                { label: 'Signed', value: result.c2pa.signed ? 'Yes' : 'No', ok: result.c2pa.signed },
                { label: 'Trusted', value: result.c2pa.trusted ? 'Yes' : 'No', ok: result.c2pa.trusted },
                { label: 'Provider', value: result.c2pa.provider || '—', ok: null },
                { label: 'Claim Generator', value: result.c2pa.claim_generator || '—', ok: null },
                { label: 'Assertions', value: result.c2pa.assertions.length > 0 ? result.c2pa.assertions.join(', ') : 'None', ok: null },
              ].map(item => (
                <div key={item.label} className="bg-slate-800/40 rounded-xl p-4 border border-slate-700/60">
                  <div className="text-xs text-slate-500 mb-1">{item.label}</div>
                  <div className="flex items-center gap-1.5">
                    {item.ok !== null && (
                      item.ok
                        ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                        : <AlertTriangle className="w-3.5 h-3.5 text-red-400 flex-shrink-0" />
                    )}
                    <span className="text-sm text-slate-200 font-medium truncate">{item.value}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Metadata */}
      <div className="card overflow-hidden">
        <button
          onClick={() => setMetaExpanded(!metaExpanded)}
          className="w-full px-6 py-4 border-b border-slate-800 flex items-center gap-2 hover:bg-slate-800/30 transition-colors"
        >
          <Info className="w-5 h-5 text-indigo-400" />
          <h2 className="font-semibold text-white">Extracted Metadata</h2>
          {result.metadata.filter(m => m.suspicious).length > 0 && (
            <span className="ml-2 px-2 py-0.5 rounded-full text-xs font-bold bg-orange-500/15 text-orange-400">
              {result.metadata.filter(m => m.suspicious).length} suspicious
            </span>
          )}
          <span className="ml-auto text-xs text-slate-500 mr-2">{result.metadata.length} fields</span>
          {metaExpanded ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
        </button>
        {metaExpanded && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-800/60">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">Field</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">Value</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">Flag</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {result.metadata.map((m, i) => (
                  <tr key={i} className={m.suspicious ? 'bg-orange-900/10' : 'hover:bg-slate-800/20'}>
                    <td className="px-6 py-3 font-medium text-slate-300 whitespace-nowrap">{m.key}</td>
                    <td className="px-6 py-3 text-slate-400 max-w-sm">
                      <div className="truncate">{m.value}</div>
                      {m.note && <div className="text-xs text-orange-400 mt-0.5">{m.note}</div>}
                    </td>
                    <td className="px-6 py-3">
                      {m.suspicious ? (
                        <span className="inline-flex items-center gap-1 text-orange-400 text-xs font-bold">
                          <AlertTriangle className="w-3.5 h-3.5" /> Suspicious
                        </span>
                      ) : (
                        <span className="text-slate-600 text-xs">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Footer note */}
      <p className="text-xs text-slate-600 text-center pb-4">
        Job ID: {result.job_id} · Analyzed {new Date(result.analyzed_at).toLocaleString()} ·
        Results are probabilistic — combine with human review for high-stakes decisions.
      </p>
    </div>
  )
}
