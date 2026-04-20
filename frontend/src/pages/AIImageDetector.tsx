import SEOLandingTemplate from '../components/SEOLandingTemplate'

const RELATED = [
  { href: '/chatgpt-detector', label: 'ChatGPT Detector' },
  { href: '/ai-writing-detector', label: 'AI Writing Detector' },
  { href: '/analyze', label: 'Full File Scanner' },
  { href: '/pricing', label: 'Pricing' },
]

const SCHEMA = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'SoftwareApplication',
      name: 'VeritasAI AI Image Detector',
      applicationCategory: 'SecurityApplication',
      operatingSystem: 'Web',
      url: 'https://veritasartificialis.com/ai-image-detector',
      description: 'Free online tool to detect AI-generated images from Midjourney, DALL-E, Stable Diffusion and deepfakes.',
      offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
    },
    {
      '@type': 'FAQPage',
      mainEntity: [
        {
          '@type': 'Question',
          name: 'Can VeritasAI detect Midjourney and DALL-E images?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Yes. VeritasAI analyzes pixel-level noise patterns, GAN artifacts, EXIF metadata anomalies, and frequency domain signals that are characteristic of AI image generators including Midjourney, DALL-E 3, Stable Diffusion, and Adobe Firefly.',
          },
        },
        {
          '@type': 'Question',
          name: 'What image formats are supported?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'VeritasAI supports JPEG, PNG, WebP, TIFF, BMP, and GIF formats. For best results use the original uncompressed image — re-saved or heavily compressed images may affect detection accuracy.',
          },
        },
        {
          '@type': 'Question',
          name: 'How does AI image detection work?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'AI image generators leave characteristic artifacts in pixel noise patterns and frequency spectra. VeritasAI examines these along with metadata signatures, color distribution anomalies, and texture inconsistencies that distinguish AI-generated images from photographs.',
          },
        },
      ],
    },
  ],
}

export default function AIImageDetector() {
  return (
    <SEOLandingTemplate config={{
      title: 'AI Image Detector — Spot Midjourney, DALL-E & Deepfakes | VeritasAI',
      description: 'Detect AI-generated images from Midjourney, DALL-E 3, Stable Diffusion and deepfakes with forensic pixel analysis. Free online AI image detector — upload JPEG, PNG, WebP instantly.',
      canonical: 'https://veritasartificialis.com/ai-image-detector',
      keywords: 'AI image detector, Midjourney detector, DALL-E detector, deepfake detector, Stable Diffusion detector, fake image detector, AI generated image checker, detect AI art',
      schema: SCHEMA,
      badge: '🖼️ AI Image & Deepfake Detection',
      heroTitle: 'Detect AI-Generated',
      heroHighlight: 'Images & Deepfakes',
      heroSubtitle: 'Upload any image to instantly detect if it was created by Midjourney, DALL-E 3, Stable Diffusion, Adobe Firefly, or other AI art generators. Advanced pixel-level forensic analysis.',
      ctaLabel: 'Check Image for AI',
      features: [
        {
          icon: '🔬',
          title: 'Pixel Noise Analysis',
          desc: 'AI image generators leave characteristic patterns in pixel noise that are invisible to the human eye but detectable with statistical analysis. VeritasAI examines these signatures.',
        },
        {
          icon: '📡',
          title: 'Frequency Domain Forensics',
          desc: 'Analyzes the DCT and FFT frequency spectrum of images. GAN and diffusion model artifacts appear as distinctive patterns in frequency space, even after JPEG compression.',
        },
        {
          icon: '📋',
          title: 'EXIF Metadata Inspection',
          desc: 'Real photos contain rich camera metadata (GPS, shutter speed, ISO, lens data). AI-generated images often have missing, inconsistent, or fabricated EXIF data.',
        },
        {
          icon: '🎨',
          title: 'Color Distribution Analysis',
          desc: 'AI models produce images with subtly different color histograms and saturation patterns compared to real photographs. VeritasAI quantifies these statistical differences.',
        },
        {
          icon: '👁️',
          title: 'Deepfake Detection',
          desc: 'Detects facial manipulation and deepfake imagery by analyzing facial geometry consistency, edge artifacts, and blending boundaries in portrait images.',
        },
        {
          icon: '⚡',
          title: 'Supports All Major Formats',
          desc: 'Upload JPEG, PNG, WebP, TIFF, BMP, or GIF. Processes images up to 10MB. For best results use the original uncompressed file.',
        },
      ],
      howItWorks: [
        'Upload your image (JPEG, PNG, WebP, TIFF) — drag and drop or click to browse.',
        'VeritasAI runs pixel noise analysis, frequency domain forensics, and metadata inspection on the full-resolution file.',
        'Get an AI probability score with a breakdown of detected signals, metadata findings, and a risk verdict.',
      ],
      faqs: [
        { q: 'Can it detect Midjourney and DALL-E images?', a: 'Yes. VeritasAI detects images from Midjourney, DALL-E 3, Stable Diffusion, Adobe Firefly, and other AI generators by analyzing pixel noise patterns, GAN artifacts, EXIF anomalies, and frequency domain signals.' },
        { q: 'What image formats are supported?', a: 'JPEG, PNG, WebP, TIFF, BMP, and GIF. For best results, use the original uncompressed image. Heavy re-compression can affect detection accuracy.' },
        { q: 'Does it detect deepfakes?', a: 'Yes. For portrait images, VeritasAI checks facial geometry consistency, blending artifacts, and edge patterns that are characteristic of deepfake and face-swap tools.' },
        { q: 'How does AI image detection work?', a: 'AI image generators leave characteristic artifacts in pixel noise patterns and frequency spectra. VeritasAI examines these alongside metadata signatures and color distribution anomalies that distinguish AI art from real photographs.' },
        { q: 'Can it detect AI images that have been edited in Photoshop?', a: 'Post-processing and editing reduce detection confidence. VeritasAI still analyzes what signals remain, but the score may be lower for heavily edited images. Metadata inspection can reveal editing history.' },
        { q: 'Is the AI image detector free?', a: 'Yes. The Free plan includes 1 scan per day. Upgrade to Pro ($4.99/month) for unlimited image scans and detailed PDF forensic reports.' },
      ],
      relatedLinks: RELATED,
    }} />
  )
}
