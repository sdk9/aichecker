import { ShieldCheck } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="border-t border-slate-800 bg-slate-950 mt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-8">

          {/* Brand */}
          <div className="sm:col-span-2">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center">
                <ShieldCheck className="w-4 h-4 text-white" />
              </div>
              <span className="font-bold text-white">Veritas<span className="text-indigo-400">AI</span></span>
            </div>
            <p className="text-slate-400 text-sm leading-relaxed max-w-xs mb-4">
              Professional AI-generated content detection for enterprises, educators, and legal teams. Forensic accuracy for images and documents.
            </p>
            <p className="text-slate-500 text-xs">
              Detect AI content with confidence. Free plan available.
            </p>
          </div>

          {/* Detectors */}
          <div>
            <h4 className="text-sm font-semibold text-slate-200 mb-4">AI Detectors</h4>
            <ul className="space-y-2.5 text-sm text-slate-400">
              <li><Link to="/chatgpt-detector" className="hover:text-indigo-400 transition-colors">ChatGPT Detector</Link></li>
              <li><Link to="/ai-image-detector" className="hover:text-indigo-400 transition-colors">AI Image Detector</Link></li>
              <li><Link to="/ai-writing-detector" className="hover:text-indigo-400 transition-colors">AI Writing Detector</Link></li>
              <li><Link to="/analyze" className="hover:text-indigo-400 transition-colors">Full File Scanner</Link></li>
            </ul>
          </div>

          {/* Product */}
          <div>
            <h4 className="text-sm font-semibold text-slate-200 mb-4">Product</h4>
            <ul className="space-y-2.5 text-sm text-slate-400">
              <li><Link to="/" className="hover:text-slate-200 transition-colors">Home</Link></li>
              <li><Link to="/pricing" className="hover:text-slate-200 transition-colors">Pricing</Link></li>
              <li><Link to="/analyze" className="hover:text-slate-200 transition-colors">Detect Content</Link></li>
              <li><Link to="/signup" className="hover:text-slate-200 transition-colors">Get Started Free</Link></li>
            </ul>
          </div>

          {/* Formats & Legal */}
          <div>
            <h4 className="text-sm font-semibold text-slate-200 mb-4">Supported Formats</h4>
            <ul className="space-y-2 text-sm text-slate-500 mb-6">
              <li>Images: JPEG, PNG, WebP, TIFF</li>
              <li>Docs: PDF, DOCX</li>
              <li>Presentations: PPTX, PPT</li>
              <li>Spreadsheets: XLSX, CSV</li>
            </ul>
            <h4 className="text-sm font-semibold text-slate-200 mb-3">Legal</h4>
            <ul className="space-y-2.5 text-sm text-slate-400">
              <li><Link to="/terms" className="hover:text-slate-200 transition-colors">Terms & Conditions</Link></li>
              <li><Link to="/contact" className="hover:text-slate-200 transition-colors">Contact Us</Link></li>
            </ul>
          </div>
        </div>

        {/* SEO keyword links strip */}
        <div className="border-t border-slate-800/60 mt-10 pt-6">
          <p className="text-slate-600 text-xs mb-3">Popular tools:</p>
          <div className="flex flex-wrap gap-x-4 gap-y-2 text-xs text-slate-600">
            <Link to="/chatgpt-detector" className="hover:text-slate-400 transition-colors">ChatGPT Detector</Link>
            <Link to="/ai-image-detector" className="hover:text-slate-400 transition-colors">Midjourney Detector</Link>
            <Link to="/ai-image-detector" className="hover:text-slate-400 transition-colors">DALL-E Detector</Link>
            <Link to="/ai-writing-detector" className="hover:text-slate-400 transition-colors">AI Essay Detector</Link>
            <Link to="/ai-writing-detector" className="hover:text-slate-400 transition-colors">AI Plagiarism Checker</Link>
            <Link to="/chatgpt-detector" className="hover:text-slate-400 transition-colors">GPT-4 Detector</Link>
            <Link to="/ai-image-detector" className="hover:text-slate-400 transition-colors">Deepfake Detector</Link>
            <Link to="/ai-writing-detector" className="hover:text-slate-400 transition-colors">Turnitin Alternative</Link>
            <Link to="/analyze" className="hover:text-slate-400 transition-colors">AI Content Scanner</Link>
          </div>
        </div>

        <div className="border-t border-slate-800 mt-6 pt-6 flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-slate-500 text-xs">
            © {new Date().getFullYear()} VeritasAI. For research and compliance use.
          </p>
          <p className="text-amber-500/70 text-xs font-medium">
            Results are probabilistic — always combine with human review.
          </p>
        </div>
      </div>
    </footer>
  )
}
