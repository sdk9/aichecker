import SEOLandingTemplate from '../components/SEOLandingTemplate'

const RELATED = [
  { href: '/ai-image-detector', label: 'AI Image Detector' },
  { href: '/ai-writing-detector', label: 'AI Writing Detector' },
  { href: '/analyze', label: 'Full File Scanner' },
  { href: '/pricing', label: 'Pricing' },
]

const SCHEMA = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'SoftwareApplication',
      name: 'VeritasAI ChatGPT Detector',
      applicationCategory: 'SecurityApplication',
      operatingSystem: 'Web',
      url: 'https://veritasartificialis.com/chatgpt-detector',
      description: 'Free online tool to detect ChatGPT-generated text, GPT-4 content, and other AI-written documents.',
      offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
    },
    {
      '@type': 'FAQPage',
      mainEntity: [
        {
          '@type': 'Question',
          name: 'Can VeritasAI detect ChatGPT-generated text?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Yes. VeritasAI uses perplexity scoring, burstiness analysis, and statistical language models to identify patterns characteristic of ChatGPT (GPT-3.5 and GPT-4) output. Upload a document or paste text to get an instant AI probability score.',
          },
        },
        {
          '@type': 'Question',
          name: 'Is this ChatGPT detector free to use?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Yes. The Free plan includes 1 scan per day at no cost. Pro subscribers get unlimited scans for $4.99/month.',
          },
        },
        {
          '@type': 'Question',
          name: 'What file types does the ChatGPT detector support?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'VeritasAI supports PDF, DOCX, PPTX, XLSX, and plain text files. You can also analyze images. The system extracts all text content before running the AI detection analysis.',
          },
        },
        {
          '@type': 'Question',
          name: 'How accurate is the ChatGPT detector?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Accuracy depends on text length and the specific model used. Longer texts (200+ words) yield more reliable scores. VeritasAI combines multiple detection signals — perplexity, burstiness, stylometric analysis — to reduce false positives. Results are probabilistic and should always be combined with human review.',
          },
        },
        {
          '@type': 'Question',
          name: 'Can it detect GPT-4 and Claude AI text?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Yes. VeritasAI is trained on output patterns from multiple large language models including GPT-4, GPT-3.5, Claude, and Gemini. The detector analyzes statistical properties that are common across AI-generated text regardless of the specific model used.',
          },
        },
      ],
    },
  ],
}

export default function ChatGPTDetector() {
  return (
    <SEOLandingTemplate config={{
      title: 'Free ChatGPT Detector — Detect GPT-4 & AI-Written Text | VeritasAI',
      description: 'Detect ChatGPT, GPT-4, and AI-generated text instantly. Free online ChatGPT detector for PDFs, Word documents, essays, and presentations. Trusted by educators, HR teams, and legal professionals.',
      canonical: 'https://veritasartificialis.com/chatgpt-detector',
      keywords: 'ChatGPT detector, GPT-4 detector, AI text detector, detect ChatGPT, AI writing checker, GPT detector free, is this ChatGPT, AI generated text checker',
      schema: SCHEMA,
      badge: '🔍 ChatGPT & GPT-4 Detection',
      heroTitle: 'Detect ChatGPT &',
      heroHighlight: 'AI-Written Text Instantly',
      heroSubtitle: 'Upload a PDF, Word document, or essay to instantly check if it was written by ChatGPT, GPT-4, Claude, or any other AI language model. Get a detailed probability report in seconds.',
      ctaLabel: 'Check for ChatGPT',
      features: [
        {
          icon: '📊',
          title: 'Perplexity Scoring',
          desc: 'Measures how surprising the text is to a language model. AI-generated text has characteristically low perplexity — it is highly predictable and uniform.',
        },
        {
          icon: '🌊',
          title: 'Burstiness Analysis',
          desc: 'Human writing has high burstiness — sentence lengths vary greatly. ChatGPT produces text with suspiciously consistent sentence length and structure.',
        },
        {
          icon: '🧬',
          title: 'Stylometric Fingerprinting',
          desc: 'Analyzes vocabulary diversity, repetition patterns, and phrasing habits. AI models leave consistent stylistic signatures that VeritasAI can identify.',
        },
        {
          icon: '📄',
          title: 'Full Document Support',
          desc: 'Upload PDFs, DOCX, PPTX, XLSX files. VeritasAI extracts text from every page and runs analysis across the entire document, not just a sample.',
        },
        {
          icon: '⚡',
          title: 'Instant Results',
          desc: 'Get an AI probability score, risk level, and confidence breakdown in seconds. No waiting, no queues.',
        },
        {
          icon: '📋',
          title: 'Downloadable Report',
          desc: 'Pro users get a full PDF forensic report with signal breakdown, evidence highlights, and a summary suitable for academic or HR proceedings.',
        },
      ],
      howItWorks: [
        'Upload your document (PDF, DOCX, PPTX, XLSX) or paste text directly into the scanner.',
        'VeritasAI runs perplexity scoring, burstiness analysis, and stylometric fingerprinting across the full content.',
        'Receive an AI probability score (0–100%) with a detailed signal breakdown and risk verdict in seconds.',
      ],
      faqs: [
        { q: 'Can VeritasAI detect ChatGPT-generated text?', a: 'Yes. VeritasAI uses perplexity scoring, burstiness analysis, and statistical language models to identify patterns characteristic of ChatGPT (GPT-3.5 and GPT-4) output. Upload a document or paste text to get an instant AI probability score.' },
        { q: 'Is this ChatGPT detector free?', a: 'Yes. The Free plan includes 1 scan per day at no cost. Pro subscribers get unlimited scans for $4.99/month — ideal for teachers, HR managers, or compliance teams.' },
        { q: 'What file types does it support?', a: 'PDF, DOCX, PPTX, XLSX, CSV, and plain text. The system extracts all text content before running AI detection analysis, so you get full-document coverage.' },
        { q: 'How accurate is the ChatGPT detector?', a: 'Accuracy improves with longer texts (200+ words). VeritasAI combines multiple signals to reduce false positives. Results are probabilistic — always combine with human review, especially for academic or legal decisions.' },
        { q: 'Can it detect GPT-4, Claude, and Gemini AI text?', a: 'Yes. VeritasAI is trained on output from multiple LLMs including GPT-4, GPT-3.5, Claude, and Gemini. The statistical patterns it detects are common across AI models, not tied to any single system.' },
        { q: 'Does paraphrasing fool the detector?', a: 'Lightly paraphrased AI text often retains the same statistical properties. Heavy paraphrasing can reduce detection accuracy, which is why VeritasAI uses multiple independent signals rather than a single score.' },
      ],
      relatedLinks: RELATED,
    }} />
  )
}
