import { useState, useCallback, useRef } from 'react'
import { useSEO } from '../hooks/useSEO'
import { motion, AnimatePresence } from 'framer-motion'
import { Link } from 'react-router-dom'
import { ShieldCheck, ArrowRight } from 'lucide-react'
import axios from 'axios'
import { AnalysisResult } from '../types/analysis'
import UploadZone from '../components/UploadZone'
import AnalysisProgress from '../components/AnalysisProgress'
import ResultsDashboard from '../components/ResultsDashboard'
import { useAuth } from '../context/AuthContext'

type Stage = 'upload' | 'analyzing' | 'results'

export default function Analyze() {
  useSEO({
    title: 'Detect AI Content — Upload File or Paste Text | VeritasAI',
    description: 'Upload an image, PDF, Word document, or presentation to instantly detect AI-generated content with forensic accuracy. Free to try.',
    canonical: 'https://veritasartificialis.com/analyze',
    keywords: 'detect AI content, AI file scanner, upload AI detector, ChatGPT document detector',
    schema: {
      '@context': 'https://schema.org',
      '@type': 'WebPage',
      name: 'VeritasAI — Detect AI Content',
      url: 'https://veritasartificialis.com/analyze',
      description: 'Upload a file to detect AI-generated content.',
    },
  })

  const { user } = useAuth()
  const [stage, setStage] = useState<Stage>('upload')
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  const [progressLabel, setProgressLabel] = useState('')
  const abortRef = useRef<AbortController | null>(null)

  const handleFile = useCallback(async (file: File) => {
    setError(null)
    setStage('analyzing')
    setProgress(0)

    abortRef.current = new AbortController()

    try {
      // Simulate staged progress
      const stages = [
        [10, 'Uploading file...'],
        [30, 'Extracting metadata...'],
        [50, 'Checking C2PA credentials...'],
        [70, 'Running AI detection...'],
        [88, 'Scoring signals...'],
        [95, 'Generating report...'],
      ] as [number, string][]

      let stageIdx = 0
      const progressInterval = setInterval(() => {
        if (stageIdx < stages.length) {
          setProgress(stages[stageIdx][0])
          setProgressLabel(stages[stageIdx][1])
          stageIdx++
        }
      }, 400)

      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post<AnalysisResult>('/api/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        signal: abortRef.current.signal,
      })

      clearInterval(progressInterval)
      setProgress(100)
      setProgressLabel('Analysis complete!')

      await new Promise(r => setTimeout(r, 400))
      setResult(response.data)
      setStage('results')
    } catch (err: unknown) {
      if (axios.isCancel(err)) return
      let msg = 'Analysis failed. Please try again.'
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        msg = String(err.response.data.detail)
      }
      setError(msg)
      setStage('upload')
    }
  }, [])

  const reset = useCallback(() => {
    abortRef.current?.abort()
    setStage('upload')
    setResult(null)
    setError(null)
    setProgress(0)
  }, [])

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        {/* Page header */}
        <AnimatePresence mode="wait">
          {stage !== 'results' && (
            <motion.div
              key="header"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="text-center mb-10"
            >
              <h1 className="text-3xl sm:text-4xl font-bold text-white mb-3">
                Detect AI-Generated Content
              </h1>
              <p className="text-slate-400 text-lg max-w-xl mx-auto">
                Upload any image, PDF, DOCX, PPTX, or spreadsheet for full forensic analysis.
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error banner */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 rounded-xl bg-red-900/30 border border-red-500/40 text-red-300 text-sm"
          >
            {error}
          </motion.div>
        )}

        {/* Auth gate */}
        {!user && stage === 'upload' && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="card p-10 text-center mb-6"
          >
            <div className="w-16 h-16 bg-indigo-600/20 rounded-2xl flex items-center justify-center mx-auto mb-5">
              <ShieldCheck className="w-8 h-8 text-indigo-400" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-3">Create a free account to start</h2>
            <p className="text-slate-400 text-sm leading-relaxed max-w-md mx-auto mb-7">
              Sign up for free to get 1 scan per month. Upgrade to Pro for unlimited scans at $4.99/month.
              No credit card required for the free plan.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link to="/signup" className="btn-primary inline-flex items-center justify-center gap-2 px-8 py-3">
                Create free account <ArrowRight className="w-4 h-4" />
              </Link>
              <Link to="/login" className="btn-secondary inline-flex items-center justify-center gap-2 px-8 py-3">
                Sign in
              </Link>
            </div>
          </motion.div>
        )}

        {/* Stage renderer */}
        <AnimatePresence mode="wait">
          {stage === 'upload' && user && (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <UploadZone onFile={handleFile} />
            </motion.div>
          )}

          {stage === 'analyzing' && (
            <motion.div
              key="analyzing"
              initial={{ opacity: 0, scale: 0.97 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
            >
              <AnalysisProgress progress={progress} label={progressLabel} />
            </motion.div>
          )}

          {stage === 'results' && result && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <ResultsDashboard result={result} onReset={reset} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
