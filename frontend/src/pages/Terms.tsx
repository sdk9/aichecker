import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { ShieldCheck, AlertTriangle, Scale, FileText, CreditCard, Lock, Mail } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useSEO } from '../hooks/useSEO'

const Section = ({ icon: Icon, title, children }: { icon: any; title: string; children: React.ReactNode }) => (
  <motion.div
    initial={{ opacity: 0, y: 16 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    className="mb-10"
  >
    <div className="flex items-center gap-3 mb-4">
      <div className="w-9 h-9 rounded-xl bg-indigo-500/10 flex items-center justify-center flex-shrink-0">
        <Icon className="w-5 h-5 text-indigo-400" />
      </div>
      <h2 className="text-xl font-bold text-white">{title}</h2>
    </div>
    <div className="text-slate-400 text-sm leading-relaxed space-y-3 pl-12">{children}</div>
  </motion.div>
)

export default function Terms() {
  useSEO({
    title: 'Terms & Conditions — VeritasAI',
    description:
      'Read VeritasAI\'s Terms & Conditions. Understand how our AI content detection service works, accuracy expectations (~70–85%), plan limits, payments, privacy, and acceptable use.',
    canonical: 'https://veritasartificialis.com/terms',
    ogType: 'article',
  })

  useEffect(() => {
    const script = document.createElement('script')
    script.type = 'application/ld+json'
    script.id = 'terms-jsonld'
    script.text = JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'WebPage',
      name: 'Terms & Conditions — VeritasAI',
      description:
        'VeritasAI Terms & Conditions covering service description, accuracy disclaimer, plans, payments, privacy, and acceptable use.',
      url: 'https://veritasartificialis.com/terms',
      publisher: {
        '@type': 'Organization',
        name: 'VeritasAI',
        url: 'https://veritasartificialis.com',
        contactPoint: {
          '@type': 'ContactPoint',
          email: 'contact@veritasartificialis.com',
          contactType: 'customer support',
        },
      },
      dateModified: '2025-04-01',
    })
    document.head.appendChild(script)
    return () => {
      document.getElementById('terms-jsonld')?.remove()
    }
  }, [])

  return (
    <div className="min-h-screen py-16 px-4 sm:px-6 lg:px-8 bg-slate-950">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-600/15 border border-indigo-500/30 text-indigo-300 text-sm font-medium mb-6">
            <Scale className="w-4 h-4" />
            Legal
          </div>
          <h1 className="text-4xl font-black text-white mb-4">Terms & Conditions</h1>
          <p className="text-slate-400">Last updated: April 2025</p>
        </motion.div>

        {/* Critical accuracy notice */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex items-start gap-4 p-6 rounded-2xl bg-amber-500/10 border border-amber-500/40 mb-10"
        >
          <AlertTriangle className="w-6 h-6 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-amber-300 font-bold text-base mb-2">
              Important: Results Are Probabilistic
            </p>
            <p className="text-amber-200/80 text-sm leading-relaxed">
              VeritasAI uses statistical and heuristic methods to estimate the likelihood that content
              was AI-generated. <strong className="text-amber-300">No detection result is 100% accurate.</strong> False
              positives (human content flagged as AI) and false negatives (AI content not detected) do occur.
              You must always combine VeritasAI results with independent human review before making any
              decisions about individuals, employment, admissions, legal proceedings, or any other
              consequential matter.
            </p>
            <p className="text-amber-200/80 text-sm leading-relaxed mt-2">
              <strong className="text-amber-300">Typical accuracy:</strong> ~70–85% across supported file types under standard conditions.
              Accuracy varies by content type, language, file quality, and the AI model used to generate content.
              Non-English documents, heavily edited content, and mixed-origin files may produce less reliable results.
            </p>
          </div>
        </motion.div>

        {/* Sections */}
        <Section icon={FileText} title="1. Service Description">
          <p>
            VeritasAI ("the Service", "we", "us") is a forensic AI-content detection platform operated at
            veritasartificialis.com. The Service analyses uploaded files — including images, documents,
            presentations, and spreadsheets — using statistical signals to produce an AI-probability score.
          </p>
          <p>
            The Service is intended as an <strong className="text-slate-300">assistive tool</strong> to
            help human reviewers make more informed decisions. It is not a replacement for professional
            judgment. Outputs should not be used as sole evidence in any formal or legal context.
          </p>
          <p>
            Supported file types: JPEG, PNG, WebP, GIF, TIFF, BMP, HEIC, PDF, DOCX, DOC, PPTX, PPT, XLSX, XLS, CSV.
            Maximum file size: 100 MB.
          </p>
        </Section>

        <Section icon={ShieldCheck} title="2. Accounts & Eligibility">
          <p>
            You must create a free account to use the Service. By registering, you confirm that you are at
            least 16 years old and that the information you provide is accurate.
          </p>
          <p>
            <strong className="text-slate-300">Free plan:</strong> 1 scan per calendar month. Resets on the
            first day of each month (UTC).
          </p>
          <p>
            <strong className="text-slate-300">Pro plan ($4.99/month):</strong> Unlimited scans for the
            duration of an active subscription. Subscriptions are billed monthly via Stripe and can be
            cancelled at any time from your account settings.
          </p>
          <p>
            You are responsible for keeping your login credentials secure. We are not liable for
            unauthorised access resulting from your failure to secure your account.
          </p>
        </Section>

        <Section icon={Lock} title="3. Acceptable Use">
          <p>You agree NOT to use the Service to:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Make hiring, admissions, or legal decisions based solely on VeritasAI results without human review</li>
            <li>Discriminate against individuals based on AI-probability scores alone</li>
            <li>Violate any applicable privacy, employment, or anti-discrimination laws</li>
            <li>Attempt to reverse-engineer, scrape, or attack the platform</li>
            <li>Upload files containing illegal content, malware, or content that violates third-party rights</li>
            <li>Circumvent scan limits via multiple accounts or automated abuse</li>
          </ul>
          <p>
            We reserve the right to suspend or terminate accounts that violate these terms without prior notice.
          </p>
        </Section>

        <Section icon={CreditCard} title="4. Payments & Refunds">
          <p>
            Payments for the Pro plan are processed securely by Stripe. We do not store your payment card
            details. By subscribing, you authorise Stripe to charge your payment method monthly until you cancel.
          </p>
          <p>
            <strong className="text-slate-300">Cancellation:</strong> You may cancel at any time. Your Pro
            access continues until the end of the current billing period. No partial refunds are issued for
            unused time within a billing period.
          </p>
          <p>
            If you believe you have been charged in error, contact us at{' '}
            <a href="mailto:contact@veritasartificialis.com" className="text-indigo-400 hover:text-indigo-300">
              contact@veritasartificialis.com
            </a>{' '}
            within 14 days of the charge.
          </p>
        </Section>

        <Section icon={ShieldCheck} title="5. Privacy & Data Handling">
          <p>
            <strong className="text-slate-300">Uploaded files:</strong> Files you upload are processed
            in-memory and on temporary server storage solely for the purpose of analysis. They are deleted
            from server storage immediately after analysis is complete.
          </p>
          <p>
            <strong className="text-slate-300">Account data:</strong> We store your email address, hashed
            password, plan status, and usage counters. We do not sell your personal data to third parties.
          </p>
          <p>
            <strong className="text-slate-300">Analysis results:</strong> Results are temporarily cached
            in-memory for PDF report generation (up to 1 hour after analysis) and are not stored
            permanently on our servers.
          </p>
          <p>
            We use Stripe for payment processing. Stripe's privacy policy governs how Stripe handles
            payment information.
          </p>
        </Section>

        <Section icon={AlertTriangle} title="6. Disclaimer of Warranties & Liability">
          <p>
            THE SERVICE IS PROVIDED "AS IS" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED. WE DO NOT
            WARRANT THAT THE SERVICE WILL BE ERROR-FREE, UNINTERRUPTED, OR THAT RESULTS WILL BE ACCURATE
            FOR ANY PARTICULAR USE CASE.
          </p>
          <p>
            TO THE MAXIMUM EXTENT PERMITTED BY LAW, VERITASAI SHALL NOT BE LIABLE FOR ANY INDIRECT,
            INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES ARISING FROM YOUR USE OF THE SERVICE, INCLUDING
            BUT NOT LIMITED TO EMPLOYMENT DECISIONS, LEGAL DISPUTES, REPUTATIONAL HARM, OR DATA LOSS.
          </p>
          <p>
            Our total aggregate liability for any claim arising from use of the Service shall not exceed the
            amount you paid to us in the 3 months preceding the claim, or $15, whichever is greater.
          </p>
        </Section>

        <Section icon={Scale} title="7. Changes to These Terms">
          <p>
            We may update these Terms from time to time. Material changes will be communicated by email
            or prominent notice on the website at least 14 days before taking effect. Continued use of the
            Service after changes take effect constitutes acceptance.
          </p>
          <p>
            These Terms are governed by the laws of the jurisdiction in which VeritasAI operates, without
            regard to conflict of law provisions.
          </p>
        </Section>

        <Section icon={Mail} title="8. Contact">
          <p>
            For questions about these Terms, support requests, or account issues, contact us at:
          </p>
          <p>
            <a
              href="mailto:contact@veritasartificialis.com"
              className="text-indigo-400 hover:text-indigo-300 font-medium"
            >
              contact@veritasartificialis.com
            </a>
          </p>
        </Section>

        <div className="border-t border-slate-800 pt-8 text-center">
          <p className="text-slate-500 text-sm mb-4">
            By using VeritasAI, you agree to these Terms & Conditions.
          </p>
          <Link to="/" className="btn-secondary text-sm px-6 py-2.5">
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  )
}
