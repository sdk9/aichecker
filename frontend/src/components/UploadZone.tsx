import { useCallback, useState } from 'react'
import { motion } from 'framer-motion'
import { Upload, ImageIcon, Video, Music, FileText, AlertCircle } from 'lucide-react'

const ACCEPT = '.jpg,.jpeg,.png,.webp,.gif,.tiff,.bmp,.heic,.mp4,.mov,.avi,.webm,.mkv,.mp3,.wav,.ogg,.flac,.aac,.m4a,.pdf,.docx,.doc'
const MAX_MB = 100

interface Props {
  onFile: (file: File) => void
}

export default function UploadZone({ onFile }: Props) {
  const [dragging, setDragging] = useState(false)
  const [sizeError, setSizeError] = useState(false)

  const handle = useCallback((file: File) => {
    if (file.size > MAX_MB * 1024 * 1024) {
      setSizeError(true)
      return
    }
    setSizeError(false)
    onFile(file)
  }, [onFile])

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handle(file)
  }, [handle])

  const onInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handle(file)
  }, [handle])

  return (
    <div className="space-y-6">
      {/* Drop zone */}
      <motion.label
        htmlFor="file-upload"
        className={`
          relative flex flex-col items-center justify-center w-full min-h-80 rounded-2xl border-2 border-dashed
          cursor-pointer transition-all duration-200 overflow-hidden
          ${dragging
            ? 'border-indigo-400 bg-indigo-600/10 scale-[1.01]'
            : 'border-slate-700 bg-slate-900/50 hover:border-indigo-500/60 hover:bg-slate-900'
          }
        `}
        onDragEnter={() => setDragging(true)}
        onDragLeave={() => setDragging(false)}
        onDragOver={e => e.preventDefault()}
        onDrop={onDrop}
        whileHover={{ scale: 1.005 }}
        whileTap={{ scale: 0.998 }}
      >
        {/* Glow */}
        {dragging && (
          <div className="absolute inset-0 bg-indigo-600/5 rounded-2xl pointer-events-none" />
        )}

        <div className="flex flex-col items-center gap-5 text-center p-8 z-10">
          <motion.div
            animate={dragging ? { scale: 1.15, rotate: 5 } : { scale: 1, rotate: 0 }}
            transition={{ type: 'spring', stiffness: 300 }}
            className="w-16 h-16 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center"
          >
            <Upload className="w-8 h-8 text-indigo-400" />
          </motion.div>

          <div>
            <p className="text-lg font-semibold text-slate-200 mb-1">
              {dragging ? 'Drop to analyze' : 'Drop a file or click to upload'}
            </p>
            <p className="text-sm text-slate-500">
              Supports images, video, audio, PDF, and DOCX · Max {MAX_MB} MB
            </p>
          </div>

          <div className="flex flex-wrap justify-center gap-2">
            {[
              { icon: ImageIcon, label: 'JPG / PNG / WebP', color: 'text-blue-400' },
              { icon: Video, label: 'MP4 / MOV', color: 'text-purple-400' },
              { icon: Music, label: 'MP3 / WAV / FLAC', color: 'text-pink-400' },
              { icon: FileText, label: 'PDF / DOCX', color: 'text-emerald-400' },
            ].map(({ icon: Icon, label, color }) => (
              <div
                key={label}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-800 text-xs text-slate-300"
              >
                <Icon className={`w-3.5 h-3.5 ${color}`} />
                {label}
              </div>
            ))}
          </div>
        </div>

        <input
          id="file-upload"
          type="file"
          accept={ACCEPT}
          className="sr-only"
          onChange={onInputChange}
        />
      </motion.label>

      {/* Size error */}
      {sizeError && (
        <motion.div
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-2 p-4 rounded-xl bg-red-900/30 border border-red-500/40 text-red-300 text-sm"
        >
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          File exceeds {MAX_MB} MB limit. Please use a smaller file.
        </motion.div>
      )}

      {/* Example tiles */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4">
        {[
          {
            icon: ImageIcon,
            title: 'AI Portrait Check',
            desc: 'Detect Midjourney, DALL-E, and Stable Diffusion generated faces.',
            color: 'text-blue-400',
            bg: 'bg-blue-500/10',
          },
          {
            icon: FileText,
            title: 'Essay Authenticity',
            desc: 'Score burstiness, TTR, and AI phrase density in DOCX or PDF.',
            color: 'text-emerald-400',
            bg: 'bg-emerald-500/10',
          },
          {
            icon: Music,
            title: 'Voice Clone Detection',
            desc: 'Identify synthetic audio from ElevenLabs, Bark, and similar tools.',
            color: 'text-pink-400',
            bg: 'bg-pink-500/10',
          },
        ].map(item => (
          <div key={item.title} className="card p-5">
            <div className={`${item.bg} rounded-xl w-10 h-10 flex items-center justify-center mb-3`}>
              <item.icon className={`w-5 h-5 ${item.color}`} />
            </div>
            <h3 className="font-semibold text-slate-200 text-sm mb-1">{item.title}</h3>
            <p className="text-slate-500 text-xs leading-relaxed">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
