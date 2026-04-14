import { motion } from 'framer-motion'
import { Cpu } from 'lucide-react'

interface Props {
  progress: number
  label: string
}

export default function AnalysisProgress({ progress, label }: Props) {
  return (
    <div className="flex flex-col items-center justify-center min-h-96 py-16">
      {/* Animated ring */}
      <div className="relative mb-8">
        <motion.div
          className="w-28 h-28 rounded-full border-4 border-indigo-600/20"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
        />
        <motion.div
          className="absolute inset-0 w-28 h-28 rounded-full border-4 border-t-indigo-500 border-r-purple-500 border-b-transparent border-l-transparent"
          animate={{ rotate: 360 }}
          transition={{ duration: 1.2, repeat: Infinity, ease: 'linear' }}
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <Cpu className="w-8 h-8 text-indigo-400" />
        </div>
      </div>

      <h2 className="text-xl font-bold text-white mb-2">Analyzing file</h2>
      <p className="text-slate-400 text-sm mb-8">{label || 'Processing...'}</p>

      {/* Progress bar */}
      <div className="w-72">
        <div className="flex justify-between text-xs text-slate-500 mb-2">
          <span>Progress</span>
          <span>{progress}%</span>
        </div>
        <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ ease: 'easeOut' }}
          />
        </div>
      </div>

      {/* Stage indicators */}
      <div className="flex gap-2 mt-8">
        {['Metadata', 'C2PA', 'AI Detection', 'Scoring', 'Report'].map((stage, i) => (
          <div
            key={stage}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
              progress >= (i + 1) * 18
                ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/30'
                : 'bg-slate-800 text-slate-500'
            }`}
          >
            {stage}
          </div>
        ))}
      </div>
    </div>
  )
}
