import { motion } from 'framer-motion'
import { Code2, Terminal, Copy, CheckCircle2, Zap } from 'lucide-react'
import { useState } from 'react'

function CodeBlock({ code, lang = 'bash' }: { code: string; lang?: string }) {
  const [copied, setCopied] = useState(false)
  const copy = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <div className="relative group">
      <div className="rounded-xl bg-slate-950 border border-slate-800 overflow-hidden">
        <div className="flex items-center justify-between px-4 py-2 bg-slate-900 border-b border-slate-800">
          <span className="text-xs text-slate-500 font-mono">{lang}</span>
          <button
            onClick={copy}
            className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-200 transition-colors"
          >
            {copied ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            {copied ? 'Copied' : 'Copy'}
          </button>
        </div>
        <pre className="px-5 py-4 text-sm text-slate-300 font-mono overflow-x-auto leading-relaxed whitespace-pre">
          <code>{code}</code>
        </pre>
      </div>
    </div>
  )
}

export default function ApiDocs() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-12">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center">
            <Code2 className="w-5 h-5 text-indigo-400" />
          </div>
          <h1 className="text-3xl font-bold text-white">API Reference</h1>
        </div>
        <p className="text-slate-400 text-lg max-w-2xl">
          Integrate VeritasAI into your upload pipeline, compliance workflow, or content moderation system.
          All endpoints accept multipart file uploads and return structured JSON.
        </p>

        <div className="mt-4 flex flex-wrap gap-2">
          <span className="px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-400 text-xs font-bold">REST API</span>
          <span className="px-3 py-1 rounded-full bg-indigo-500/15 text-indigo-400 text-xs font-bold">JSON Responses</span>
          <span className="px-3 py-1 rounded-full bg-purple-500/15 text-purple-400 text-xs font-bold">Multipart Upload</span>
          <span className="px-3 py-1 rounded-full bg-blue-500/15 text-blue-400 text-xs font-bold">PDF Reports</span>
        </div>
      </motion.div>

      {/* Base URL */}
      <section>
        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <Terminal className="w-5 h-5 text-indigo-400" />
          Base URL
        </h2>
        <CodeBlock code="http://localhost:8000" lang="url" />
        <p className="text-slate-500 text-sm mt-3">
          In production, replace with your deployed domain. Interactive docs available at{' '}
          <code className="text-indigo-400 bg-slate-900 px-1.5 py-0.5 rounded text-xs">/api/docs</code>
        </p>
      </section>

      {/* Endpoints */}
      <section className="space-y-8">
        <h2 className="text-xl font-bold text-white">Endpoints</h2>

        {/* POST /api/analyze */}
        <div className="card overflow-hidden">
          <div className="px-6 py-4 bg-slate-800/60 border-b border-slate-800 flex items-center gap-3">
            <span className="px-2.5 py-1 rounded-lg bg-blue-500/20 text-blue-400 text-xs font-black font-mono">POST</span>
            <code className="text-slate-200 font-mono text-sm">/api/analyze</code>
            <span className="ml-auto text-xs text-slate-500">Analyze a file</span>
          </div>
          <div className="p-6 space-y-6">
            <p className="text-slate-400 text-sm">
              Upload a file for full forensic analysis. Returns a structured result with AI probability,
              detection signals, metadata, C2PA status, and a job ID for downloading the PDF report.
            </p>

            <div>
              <h4 className="text-sm font-semibold text-slate-200 mb-2">Request — multipart/form-data</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left bg-slate-800/60">
                      <th className="px-4 py-2 text-xs text-slate-400 font-semibold">Field</th>
                      <th className="px-4 py-2 text-xs text-slate-400 font-semibold">Type</th>
                      <th className="px-4 py-2 text-xs text-slate-400 font-semibold">Required</th>
                      <th className="px-4 py-2 text-xs text-slate-400 font-semibold">Description</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    <tr>
                      <td className="px-4 py-3 font-mono text-indigo-400 text-xs">file</td>
                      <td className="px-4 py-3 text-slate-400 text-xs">File</td>
                      <td className="px-4 py-3"><span className="text-emerald-400 text-xs font-bold">Yes</span></td>
                      <td className="px-4 py-3 text-slate-400 text-xs">Image, video, audio, PDF, or DOCX. Max 100 MB.</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3 font-mono text-indigo-400 text-xs">niche</td>
                      <td className="px-4 py-3 text-slate-400 text-xs">string</td>
                      <td className="px-4 py-3"><span className="text-slate-500 text-xs">No</span></td>
                      <td className="px-4 py-3 text-slate-400 text-xs">
                        Context hint: <code className="bg-slate-800 px-1 rounded">hr</code>, <code className="bg-slate-800 px-1 rounded">marketplace</code>,{' '}
                        <code className="bg-slate-800 px-1 rounded">education</code>, <code className="bg-slate-800 px-1 rounded">media</code>,{' '}
                        <code className="bg-slate-800 px-1 rounded">legal</code>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-semibold text-slate-200 mb-3">cURL example</h4>
              <CodeBlock lang="bash" code={`curl -X POST http://localhost:8000/api/analyze \\
  -F "file=@portrait.jpg" \\
  -F "niche=hr"`} />
            </div>

            <div>
              <h4 className="text-sm font-semibold text-slate-200 mb-3">Python example</h4>
              <CodeBlock lang="python" code={`import requests

with open("portrait.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/analyze",
        files={"file": ("portrait.jpg", f, "image/jpeg")},
        data={"niche": "hr"},
    )

result = response.json()
print(f"Verdict: {result['verdict']}")
print(f"AI Probability: {result['ai_probability'] * 100:.1f}%")
print(f"Report: /api/report/{result['job_id']}")`} />
            </div>

            <div>
              <h4 className="text-sm font-semibold text-slate-200 mb-3">Response schema</h4>
              <CodeBlock lang="json" code={`{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "portrait.jpg",
  "file_type": "image",
  "file_size_bytes": 245760,
  "mime_type": "image/jpeg",

  "ai_probability": 0.87,
  "confidence": 0.82,
  "verdict": "AI-Generated",
  "verdict_color": "red",

  "signals": [
    {
      "name": "No EXIF Metadata",
      "description": "File contains zero EXIF data...",
      "severity": "high",
      "score": 0.80,
      "details": "AI generators produce images without camera metadata."
    }
  ],

  "metadata": [
    { "key": "File Size", "value": "245,760 bytes", "suspicious": false },
    { "key": "EXIF Data", "value": "None found", "suspicious": true,
      "note": "Missing EXIF is common in AI-generated images" }
  ],

  "c2pa": {
    "has_credentials": false,
    "provider": null,
    "signed": false,
    "trusted": false,
    "assertions": [],
    "note": "No C2PA Content Credentials found."
  },

  "metadata_score": 0.80,
  "artifact_score": 0.75,
  "frequency_score": 0.70,
  "consistency_score": 0.82,

  "analysis_duration_ms": 312,
  "analyzed_at": "2025-04-13T12:00:00+00:00",
  "report_available": true
}`} />
            </div>
          </div>
        </div>

        {/* GET /api/report */}
        <div className="card overflow-hidden">
          <div className="px-6 py-4 bg-slate-800/60 border-b border-slate-800 flex items-center gap-3">
            <span className="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-400 text-xs font-black font-mono">GET</span>
            <code className="text-slate-200 font-mono text-sm">/api/report/{'{job_id}'}</code>
            <span className="ml-auto text-xs text-slate-500">Download PDF report</span>
          </div>
          <div className="p-6 space-y-4">
            <p className="text-slate-400 text-sm">
              Download the professional PDF forensic report for a previously analyzed file.
              Returns <code className="text-indigo-400 bg-slate-900 px-1.5 py-0.5 rounded text-xs">application/pdf</code>.
            </p>
            <CodeBlock lang="bash" code={`curl http://localhost:8000/api/report/550e8400-e29b-41d4-a716-446655440000 \\
  -o forensic_report.pdf`} />
          </div>
        </div>

        {/* GET /api/result */}
        <div className="card overflow-hidden">
          <div className="px-6 py-4 bg-slate-800/60 border-b border-slate-800 flex items-center gap-3">
            <span className="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-400 text-xs font-black font-mono">GET</span>
            <code className="text-slate-200 font-mono text-sm">/api/result/{'{job_id}'}</code>
            <span className="ml-auto text-xs text-slate-500">Retrieve cached result</span>
          </div>
          <div className="p-6">
            <p className="text-slate-400 text-sm">
              Retrieve the full JSON result for a job. Results are cached in memory for the current server session.
            </p>
          </div>
        </div>

        {/* GET /api/health */}
        <div className="card overflow-hidden">
          <div className="px-6 py-4 bg-slate-800/60 border-b border-slate-800 flex items-center gap-3">
            <span className="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-400 text-xs font-black font-mono">GET</span>
            <code className="text-slate-200 font-mono text-sm">/api/health</code>
            <span className="ml-auto text-xs text-slate-500">Health check</span>
          </div>
          <div className="p-6">
            <CodeBlock lang="json" code={`{ "status": "ok", "service": "VeritasAI" }`} />
          </div>
        </div>
      </section>

      {/* Supported formats */}
      <section>
        <h2 className="text-xl font-bold text-white mb-4">Supported File Types</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {[
            { type: 'Images', formats: 'JPEG, PNG, WebP, GIF, TIFF, BMP, HEIC/HEIF', analysis: 'ELA, DCT, noise, color, EXIF, C2PA' },
            { type: 'Video', formats: 'MP4, MOV, AVI, WebM, MKV', analysis: 'Frame extraction, container metadata, C2PA' },
            { type: 'Audio', formats: 'MP3, WAV, OGG, FLAC, AAC, M4A', analysis: 'Metadata, sample rate, encoder markers' },
            { type: 'Documents', formats: 'PDF, DOCX, DOC', analysis: 'Burstiness, TTR, AI phrase density, creator metadata' },
          ].map(row => (
            <div key={row.type} className="card p-5">
              <div className="font-semibold text-slate-200 mb-1">{row.type}</div>
              <div className="text-xs text-indigo-400 mb-2 font-mono">{row.formats}</div>
              <div className="text-xs text-slate-500">{row.analysis}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Rate limits */}
      <section>
        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-yellow-400" />
          Rate Limits & Constraints
        </h2>
        <div className="card p-6">
          <ul className="space-y-3 text-sm text-slate-400">
            {[
              'Max file size: 100 MB per request',
              'Analysis timeout: 60 seconds (complex video/audio may need longer)',
              'Results cached in memory for the current server session (restart clears cache)',
              'PDF reports generated synchronously and returned as binary in the report endpoint',
            ].map(item => (
              <li key={item} className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-indigo-400 flex-shrink-0 mt-0.5" />
                {item}
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* Interactive docs link */}
      <section className="card p-6 border-indigo-500/20 bg-indigo-600/5">
        <h3 className="font-semibold text-white mb-2">Interactive Swagger UI</h3>
        <p className="text-slate-400 text-sm mb-4">
          The backend serves auto-generated interactive API documentation via FastAPI.
        </p>
        <a
          href="/api/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition-colors"
        >
          <Code2 className="w-4 h-4" />
          Open Swagger UI
        </a>
      </section>
    </div>
  )
}
