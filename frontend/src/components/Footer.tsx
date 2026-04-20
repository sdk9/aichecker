import { ShieldCheck } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="border-t border-slate-800 bg-slate-950 mt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center">
                <ShieldCheck className="w-4 h-4 text-white" />
              </div>
              <span className="font-bold text-white">Veritas<span className="text-indigo-400">AI</span></span>
            </div>
            <p className="text-slate-400 text-sm leading-relaxed max-w-sm">
              Professional AI-generated content detection for enterprises.
              Protecting trust in images and documents.
            </p>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-slate-200 mb-3">Product</h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li><Link to="/analyze" className="hover:text-slate-200 transition-colors">Detect Content</Link></li>
              <li><Link to="/pricing" className="hover:text-slate-200 transition-colors">Pricing</Link></li>
              <li><Link to="/#niches" className="hover:text-slate-200 transition-colors">Use Cases</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-slate-200 mb-3">Supported Formats</h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li>Images: JPEG, PNG, WebP, TIFF</li>
              <li>Docs: PDF, DOCX</li>
              <li>Presentations: PPTX, PPT</li>
              <li>Spreadsheets: XLSX, CSV</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-800 mt-10 pt-6 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="flex flex-wrap items-center gap-4">
            <p className="text-slate-500 text-xs">
              © {new Date().getFullYear()} VeritasAI. For research and compliance use.
            </p>
            <Link to="/terms" className="text-slate-500 text-xs hover:text-slate-300 transition-colors">
              Terms & Conditions
            </Link>
            <Link to="/contact" className="text-slate-500 text-xs hover:text-slate-300 transition-colors">
              Contact Us
            </Link>
          </div>
          <p className="text-amber-500/70 text-xs font-medium">
            Results are probabilistic — always combine with human review.
          </p>
        </div>
      </div>
    </footer>
  )
}
