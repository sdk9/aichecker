import SEOLandingTemplate from '../components/SEOLandingTemplate'

const RELATED = [
  { href: '/chatgpt-detector', label: 'ChatGPT Detector' },
  { href: '/ai-image-detector', label: 'AI Image Detector' },
  { href: '/analyze', label: 'Full File Scanner' },
  { href: '/pricing', label: 'Pricing' },
]

const SCHEMA = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'SoftwareApplication',
      name: 'VeritasAI AI Writing Detector',
      applicationCategory: 'SecurityApplication',
      operatingSystem: 'Web',
      url: 'https://veritasartificialis.com/ai-writing-detector',
      description: 'Free online AI writing detector for essays, reports, articles, and academic papers. Detects ChatGPT, Claude, Gemini and other AI-written content.',
      offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
    },
    {
      '@type': 'FAQPage',
      mainEntity: [
        {
          '@type': 'Question',
          name: 'Can VeritasAI detect AI-written essays and academic papers?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Yes. VeritasAI analyzes essays, research papers, reports, and articles for statistical patterns characteristic of AI writing tools. Upload a PDF or DOCX file and receive an AI probability score in seconds.',
          },
        },
        {
          '@type': 'Question',
          name: 'Is VeritasAI better than Turnitin AI detector?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'VeritasAI uses a multi-signal approach combining perplexity scoring, burstiness analysis, vocabulary diversity metrics, and stylometric fingerprinting. Unlike single-metric detectors, this reduces false positives. VeritasAI also supports images and documents beyond plain text.',
          },
        },
        {
          '@type': 'Question',
          name: 'Can it detect AI writing in other languages?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'VeritasAI performs best on English text. Detection accuracy for other languages varies and may be lower. We are actively expanding multi-language support.',
          },
        },
      ],
    },
  ],
}

export default function AIWritingDetector() {
  return (
    <SEOLandingTemplate config={{
      title: 'AI Writing Detector — Check Essays, Reports & Articles | VeritasAI',
      description: 'Detect AI-generated essays, academic papers, reports, and articles with forensic accuracy. Free AI writing detector — supports PDF and Word documents. Trusted by educators and HR teams.',
      canonical: 'https://veritasartificialis.com/ai-writing-detector',
      keywords: 'AI writing detector, AI essay detector, detect AI writing, AI generated essay checker, AI plagiarism detector, Turnitin AI detector alternative, academic integrity tool, AI content checker',
      schema: SCHEMA,
      badge: '✍️ AI Writing & Essay Detection',
      heroTitle: 'Detect AI-Written',
      heroHighlight: 'Essays & Documents',
      heroSubtitle: 'Upload a PDF, Word document, or essay to instantly check if it was written by an AI tool. Trusted by teachers, professors, HR managers, and compliance teams. Free to try.',
      ctaLabel: 'Check for AI Writing',
      features: [
        {
          icon: '📊',
          title: 'Perplexity & Entropy Scoring',
          desc: 'AI writing is statistically predictable — it has low perplexity. VeritasAI quantifies how "surprising" text is and flags writing that falls in the characteristic AI range.',
        },
        {
          icon: '📏',
          title: 'Sentence Burstiness',
          desc: 'Humans write with varied sentence lengths — short punchy sentences followed by long complex ones. AI tools produce suspiciously uniform lengths that VeritasAI can measure and flag.',
        },
        {
          icon: '🎓',
          title: 'Academic Integrity Focus',
          desc: 'Designed for educators and academic institutions. Analyze student submissions directly from PDF or DOCX without manual copy-paste. Get a confidence score suitable for review.',
        },
        {
          icon: '📈',
          title: 'Vocabulary Diversity',
          desc: 'Measures type-token ratio and lexical sophistication. AI models tend to overuse certain phrase patterns and show characteristic vocabulary distribution that differs from human writers.',
        },
        {
          icon: '🏢',
          title: 'HR & Compliance Use Cases',
          desc: 'Check job applications, cover letters, performance reviews, and reports for AI-generated content. Ensure authentic human communication in hiring and compliance workflows.',
        },
        {
          icon: '📄',
          title: 'Multi-Format Support',
          desc: 'Upload PDF, DOCX, PPTX, XLSX, or CSV files. VeritasAI extracts and analyzes all text across every page, not just the first few paragraphs.',
        },
      ],
      howItWorks: [
        'Upload your document (PDF, DOCX, PPTX) or paste the text you want to check.',
        'VeritasAI runs perplexity scoring, burstiness analysis, vocabulary diversity metrics, and stylometric fingerprinting.',
        'Receive an AI probability percentage with a signal-by-signal breakdown and a risk verdict (Low / Medium / High).',
      ],
      faqs: [
        { q: 'Can it detect AI-written essays and academic papers?', a: 'Yes. VeritasAI analyzes essays, research papers, reports, and articles for statistical patterns characteristic of ChatGPT, Claude, Gemini, and other AI writing tools. Upload a PDF or DOCX and receive an AI probability score in seconds.' },
        { q: 'Is VeritasAI a Turnitin AI detector alternative?', a: 'VeritasAI uses a multi-signal approach — perplexity, burstiness, vocabulary diversity, stylometric fingerprinting — to reduce false positives. It also supports images and full document files, not just pasted text.' },
        { q: 'How accurate is the AI writing detector?', a: 'Accuracy improves with document length (200+ words). VeritasAI combines multiple independent signals to reduce false positives. All results are probabilistic — always combine with human review for academic or HR decisions.' },
        { q: 'Can it detect AI writing that has been edited by a human?', a: 'Lightly edited AI text often retains statistical properties that VeritasAI can detect. Heavy editing reduces accuracy, but VeritasAI\'s multi-signal approach is more robust than single-metric detectors.' },
        { q: 'Does it work with languages other than English?', a: 'VeritasAI performs best on English text. Detection accuracy for other languages varies. We are actively expanding multi-language support.' },
        { q: 'Is the AI writing detector free?', a: 'Yes. The Free plan includes 1 scan per day at no cost. Pro ($4.99/month) provides unlimited scans and PDF forensic reports — ideal for teachers, professors, and HR teams who review multiple documents daily.' },
      ],
      relatedLinks: RELATED,
    }} />
  )
}
